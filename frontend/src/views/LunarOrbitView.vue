<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { RouterLink } from "vue-router";

import { createGame, makeMove, undo } from "../api/client";
import GameBoard from "../components/GameBoard.vue";
import ResponsiveDisclosure from "../components/ResponsiveDisclosure.vue";
import GameHistoryList from "../components/game/GameHistoryList.vue";
import GameSettingsCard from "../components/game/GameSettingsCard.vue";
import GameStatusCard from "../components/game/GameStatusCard.vue";
import LunarOrbitAnalysisCard from "../components/game/LunarOrbitAnalysisCard.vue";
import type { TravelerSide } from "../types/display";
import type { GameState, Piece, Player } from "../types/game";
import {
  createPlayerDisplay,
  formatPieceFull,
  formatPieceShort,
  formatPlayer,
  pieceDisplayClass,
} from "../utils/playerDisplay";
import { useElementHeightCssVar } from "../utils/useElementHeightCssVar";
import { loadGamePreferences, saveGamePreferences } from "../utils/useGamePreferences";
import { errorText } from "../i18n/errorMap";

const gameState = ref<GameState | null>(null);
const loading = ref(false);
const errorMessage = ref("");
const savedPreferences = loadGamePreferences();
const travelerSide = ref<TravelerSide>(savedPreferences.lunarOrbit.travelerSide);
const showCellNumbers = ref(true);
const showLegalMoves = ref(true);
const showWinningMoves = ref(true);
const showThreatMoves = ref(true);
const showRemovalPreview = ref(true);
const { t } = useI18n();

const displayMap = computed(() => createPlayerDisplay(travelerSide.value, t));
const { elementRef: boardPanelRef, heightStyle: boardHeightStyle } =
  useElementHeightCssVar("--game-board-panel-height");

const canPlace = computed(() => Boolean(gameState.value && gameState.value.status === "playing" && !loading.value));
const canUndo = computed(() => Boolean(gameState.value && gameState.value.history.length > 0 && !loading.value));

const statusPillText = computed(() => {
  if (!gameState.value) {
    return "";
  }
  if (gameState.value.status !== "playing") {
    return t("game.ended");
  }
  return t("game.yourTurn", { player: formatPlayer(gameState.value.current_player, displayMap.value, t("common.none")) });
});

async function runAction(action: () => Promise<GameState>) {
  loading.value = true;
  errorMessage.value = "";
  try {
    gameState.value = await action();
  } catch (error) {
    errorMessage.value = errorText(error, t);
  } finally {
    loading.value = false;
  }
}

function startNewGame() {
  void runAction(() => createGame());
}

function undoMove() {
  if (!gameState.value) {
    return;
  }
  const gameId = gameState.value.game_id;
  void runAction(() => undo(gameId));
}

function placeAt(position: number) {
  if (!gameState.value || gameState.value.status !== "playing") {
    return;
  }
  const gameId = gameState.value.game_id;
  void runAction(() => makeMove(gameId, position));
}

function updateTravelerSide(value: TravelerSide) {
  travelerSide.value = value;
}

watch(travelerSide, () => {
  const preferences = loadGamePreferences();
  preferences.lunarOrbit = { travelerSide: travelerSide.value };
  saveGamePreferences(preferences);
});

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

onMounted(() => {
  startNewGame();
});
</script>

<template>
  <header class="app-header">
    <div class="title-block">
      <RouterLink class="return-home-link" to="/">{{ t('common.backHome') }}</RouterLink>
      <h1 class="app-title">{{ t('lunarOrbit.title') }}</h1><p class="subtitle">{{ t('lunarOrbit.subtitle') }}</p>
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
        :format-piece-label="pieceShortName"
        :format-piece-description="pieceFullName"
        :piece-class="pieceClassName"
        @place="placeAt"
      />
    </div>

    <div class="mobile-game-actions button-row" :aria-label="t('lunarOrbit.actions')">
      <button type="button" :disabled="loading" :title="t('lunarOrbit.restartTitle')" @click="startNewGame">
        {{ t('lunarOrbit.restart') }}
      </button>
      <button type="button" :disabled="loading || !canUndo" :title="t('lunarOrbit.undoTitle')" @click="undoMove">
        {{ t('lunarOrbit.undo') }}
      </button>
    </div>

    <div class="game-side-stack game-side-stack--analysis">
      <ResponsiveDisclosure
        class="disclosure-status"
        :title="t('game.status')"
        :status-text="statusPillText"
        :force-open="gameState.status === 'won'"
      >
        <GameStatusCard
          :state="gameState"
          :display-map="displayMap"
          :show-removal-preview="showRemovalPreview"
        />
      </ResponsiveDisclosure>
      <ResponsiveDisclosure class="disclosure-analysis" :title="t('analysis.title')" :default-mobile-open="true">
        <LunarOrbitAnalysisCard :state="gameState" :display-map="displayMap" />
      </ResponsiveDisclosure>
      <ResponsiveDisclosure class="disclosure-settings" :title="t('lunarOrbit.settings')">
        <GameSettingsCard
        :title="t('lunarOrbit.settings')"
        :new-game-label="t('lunarOrbit.restart')"
        :new-game-title="t('lunarOrbit.restartTitle')"
        :undo-label="t('lunarOrbit.undo')"
        :undo-title="t('lunarOrbit.undoTitle')"
        :traveler-side="travelerSide"
        :show-ai-level="false"
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

  <section v-else class="loading-panel">{{ t('common.loading') }}</section>
</template>
