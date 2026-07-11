<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import { createGame, makeAiMove, makeMove, undo } from "../api/client";
import GameBoard from "../components/GameBoard.vue";
import ResponsiveDisclosure from "../components/ResponsiveDisclosure.vue";
import GameHistoryList from "../components/game/GameHistoryList.vue";
import GameSettingsCard from "../components/game/GameSettingsCard.vue";
import GameStatusCard from "../components/game/GameStatusCard.vue";
import type { AiLevel, GameState, Piece, Player } from "../types/game";
import type { TravelerSide } from "../types/display";
import {
  createPlayerDisplay,
  formatPieceFull,
  formatPieceShort,
  formatPlayer,
  isRoleTurn,
  pieceDisplayClass,
} from "../utils/playerDisplay";
import { useElementHeightCssVar } from "../utils/useElementHeightCssVar";
import { loadGamePreferences, saveGamePreferences } from "../utils/useGamePreferences";

const THINKING_DELAYS: Record<AiLevel, { min: number; max: number }> = {
  easy: { min: 500, max: 900 },
  medium: { min: 800, max: 1400 },
  hard: { min: 1200, max: 2200 },
};

const gameState = ref<GameState | null>(null);
const loading = ref(false);
const aiThinking = ref(false);
const aiTimeoutId = ref<number | null>(null);
const errorMessage = ref("");
const savedPreferences = loadGamePreferences();
const aiLevel = ref<AiLevel>(savedPreferences.teaParty.aiLevel);
const travelerSide = ref<TravelerSide>(savedPreferences.teaParty.travelerSide);
const showCellNumbers = ref(true);
const showLegalMoves = ref(true);
const showWinningMoves = ref(true);
const showThreatMoves = ref(true);
const showRemovalPreview = ref(true);

let stateToken = 0;

const displayMap = computed(() => createPlayerDisplay(travelerSide.value));
const { elementRef: boardPanelRef, heightStyle: boardHeightStyle } =
  useElementHeightCssVar("--game-board-panel-height");

const canPlace = computed(() => {
  return Boolean(
    gameState.value &&
      gameState.value.status === "playing" &&
      !loading.value &&
      !aiThinking.value &&
      isTravelerTurn(gameState.value),
  );
});

const canUndo = computed(() => {
  if (!gameState.value || loading.value) {
    return false;
  }
  return undoCountForState(gameState.value) > 0;
});

const statusPillText = computed(() => {
  if (!gameState.value) {
    return "";
  }
  if (gameState.value.status !== "playing") {
    return "对局结束";
  }
  if (aiThinking.value) {
    return "哥伦比娅思考中……";
  }
  return `轮到 ${formatPlayer(gameState.value.current_player, displayMap.value)}`;
});

function clearAiTimeout() {
  if (aiTimeoutId.value !== null) {
    window.clearTimeout(aiTimeoutId.value);
    aiTimeoutId.value = null;
  }
}

function invalidateAiWork(): number {
  stateToken += 1;
  clearAiTimeout();
  aiThinking.value = false;
  return stateToken;
}

function isCurrentToken(token: number): boolean {
  return token === stateToken;
}

function isTravelerTurn(state: GameState): boolean {
  return state.status === "playing" && isRoleTurn(state.current_player, displayMap.value, "traveler");
}

function isColumbinaTurn(state: GameState): boolean {
  return state.status === "playing" && isRoleTurn(state.current_player, displayMap.value, "columbina");
}

function randomThinkingDelay(level: AiLevel): number {
  const range = THINKING_DELAYS[level];
  return Math.floor(range.min + Math.random() * (range.max - range.min + 1));
}

function playerName(player: Player): string {
  return formatPlayer(player, displayMap.value);
}

function pieceShortName(piece: Piece): string {
  return formatPieceShort(piece);
}

function pieceFullName(piece: Piece): string {
  return formatPieceFull(piece, displayMap.value);
}

function pieceClassName(piece: Piece): string {
  return pieceDisplayClass(piece, displayMap.value);
}

function undoCountForState(state: GameState): number {
  const lastEvent = state.history[state.history.length - 1];
  if (!lastEvent) {
    return 0;
  }

  const lastRole = displayMap.value[lastEvent.player].role;
  if (aiThinking.value && lastRole === "traveler") {
    return 1;
  }
  if (state.status !== "playing") {
    return lastRole === "traveler" ? 1 : state.history.length >= 2 ? 2 : 0;
  }
  if (isTravelerTurn(state)) {
    return state.history.length >= 2 ? 2 : 0;
  }
  if (isColumbinaTurn(state) && lastRole === "traveler") {
    return 1;
  }
  return 0;
}

async function startNewGame() {
  const token = invalidateAiWork();
  loading.value = true;
  errorMessage.value = "";
  gameState.value = null;

  try {
    const state = await createGame({ first_player: "X" });
    if (!isCurrentToken(token)) {
      return;
    }
    gameState.value = state;
    scheduleAiMoveIfNeeded(state, token);
  } catch (error) {
    if (isCurrentToken(token)) {
      errorMessage.value = error instanceof Error ? error.message : "新开棋局失败。";
    }
  } finally {
    if (isCurrentToken(token)) {
      loading.value = false;
    }
  }
}

function updateTravelerSide(value: TravelerSide) {
  if (travelerSide.value === value) {
    return;
  }
  travelerSide.value = value;
  void startNewGame();
}

function updateAiLevel(value: AiLevel) {
  aiLevel.value = value;
}

watch([travelerSide, aiLevel], () => {
  const preferences = loadGamePreferences();
  preferences.teaParty = { travelerSide: travelerSide.value, aiLevel: aiLevel.value };
  saveGamePreferences(preferences);
});

async function undoMove() {
  if (!gameState.value || loading.value) {
    return;
  }

  const undoCount = undoCountForState(gameState.value);
  if (undoCount === 0) {
    return;
  }

  const token = invalidateAiWork();
  loading.value = true;
  errorMessage.value = "";

  try {
    let state = gameState.value;
    for (let index = 0; index < undoCount; index += 1) {
      state = await undo(state.game_id);
      if (!isCurrentToken(token)) {
        return;
      }
    }
    gameState.value = state;
  } catch (error) {
    if (isCurrentToken(token)) {
      errorMessage.value = error instanceof Error ? error.message : "悔棋失败。";
    }
  } finally {
    if (isCurrentToken(token)) {
      loading.value = false;
    }
  }
}

async function placeAt(position: number) {
  if (!gameState.value || !canPlace.value) {
    return;
  }

  const token = stateToken;
  const gameId = gameState.value.game_id;
  loading.value = true;
  errorMessage.value = "";

  try {
    const state = await makeMove(gameId, position);
    if (!isCurrentToken(token)) {
      return;
    }
    gameState.value = state;
    scheduleAiMoveIfNeeded(state, token);
  } catch (error) {
    if (isCurrentToken(token)) {
      errorMessage.value = error instanceof Error ? error.message : "落子失败。";
    }
  } finally {
    if (isCurrentToken(token)) {
      loading.value = false;
    }
  }
}

function scheduleAiMoveIfNeeded(state: GameState, token = stateToken) {
  if (!isCurrentToken(token) || !isColumbinaTurn(state) || aiThinking.value) {
    return;
  }

  clearAiTimeout();
  aiThinking.value = true;
  const gameId = state.game_id;
  const moveNumber = state.move_number;
  const delay = randomThinkingDelay(aiLevel.value);
  aiTimeoutId.value = window.setTimeout(() => {
    aiTimeoutId.value = null;
    void runAiMove(gameId, moveNumber, token);
  }, delay);
}

async function runAiMove(gameId: string, moveNumber: number, token: number) {
  if (!isCurrentToken(token)) {
    return;
  }

  const state = gameState.value;
  if (!state || state.game_id !== gameId || state.move_number !== moveNumber || !isColumbinaTurn(state)) {
    aiThinking.value = false;
    return;
  }

  errorMessage.value = "";
  try {
    const response = await makeAiMove(gameId, {
      level: aiLevel.value,
      seed: null,
      auto_apply: true,
    });
    if (!isCurrentToken(token)) {
      return;
    }
    gameState.value = response.state;
  } catch (error) {
    if (isCurrentToken(token)) {
      errorMessage.value = error instanceof Error ? error.message : "哥伦比娅落子失败。";
    }
  } finally {
    if (isCurrentToken(token)) {
      aiThinking.value = false;
    }
  }
}

onMounted(() => {
  void startNewGame();
});

onBeforeUnmount(() => {
  invalidateAiWork();
});
</script>

<template>
  <header class="app-header">
    <div class="title-block">
      <RouterLink class="return-home-link" to="/">← 返回银月之庭</RouterLink>
      <h1 class="app-title">月亮棋·银月茶会</h1>
      <p class="subtitle">与银月对弈；若想取胜，须先看清哪颗月亮将要落下。</p>
    </div>
    <div v-if="gameState" class="status-pill" :class="`status-${gameState.status}`">
      <span>{{ statusPillText }}</span>
    </div>
  </header>

  <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

  <section v-if="gameState" class="game-main-layout" :style="boardHeightStyle">
    <div ref="boardPanelRef" class="game-board-slot">
      <GameBoard
        :state="gameState"
        :show-cell-numbers="showCellNumbers"
        :show-legal-moves="showLegalMoves"
        :show-winning-moves="showWinningMoves"
        :show-threat-moves="showThreatMoves"
        :show-removal-preview="showRemovalPreview"
        :disabled="!canPlace"
        :format-player="playerName"
        :format-piece-label="pieceShortName"
        :format-piece-description="pieceFullName"
        :piece-class="pieceClassName"
        @place="placeAt"
      />
    </div>

    <div class="mobile-game-actions button-row" aria-label="棋局操作">
      <button type="button" :disabled="loading" title="清空当前棋局，重新开始一场银月茶会。" @click="startNewGame">
        再启银月
      </button>
      <button type="button" :disabled="loading || !canUndo" title="沿月影回溯，撤回上一轮对弈。" @click="undoMove">
        逆转月轨
      </button>
    </div>

    <div class="game-side-stack game-side-stack--duo">
      <ResponsiveDisclosure
        class="disclosure-status"
        title="当前状态"
        :status-text="statusPillText"
        :force-open="gameState.status === 'won'"
      >
        <GameStatusCard
          :state="gameState"
          :display-map="displayMap"
          :ai-thinking="aiThinking"
          :show-removal-preview="showRemovalPreview"
        />
      </ResponsiveDisclosure>
      <ResponsiveDisclosure class="disclosure-settings" title="对弈配置">
        <GameSettingsCard
        :traveler-side="travelerSide"
        :ai-level="aiLevel"
        :show-ai-level="true"
        :loading="loading"
        :can-undo="canUndo"
        :show-cell-numbers="showCellNumbers"
        :show-legal-moves="showLegalMoves"
        :show-winning-moves="showWinningMoves"
        :show-threat-moves="showThreatMoves"
        :show-removal-preview="showRemovalPreview"
        @new-game="startNewGame"
        @undo="undoMove"
        @update:traveler-side="updateTravelerSide"
        @update:ai-level="updateAiLevel"
        @update:show-cell-numbers="showCellNumbers = $event"
        @update:show-legal-moves="showLegalMoves = $event"
        @update:show-winning-moves="showWinningMoves = $event"
        @update:show-threat-moves="showThreatMoves = $event"
        @update:show-removal-preview="showRemovalPreview = $event"
        />
      </ResponsiveDisclosure>
    </div>
  </section>

  <section v-if="gameState" class="game-history-row">
    <GameHistoryList :history="gameState.history" :display-map="displayMap" />
  </section>

  <section v-else class="loading-panel">正在连接后端...</section>
</template>
