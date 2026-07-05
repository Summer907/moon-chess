<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { createGame, getHint, makeAiMove, makeMove, undo } from "../api/client";
import AiPanel from "../components/AiPanel.vue";
import AnalysisPanel from "../components/AnalysisPanel.vue";
import ControlPanel from "../components/ControlPanel.vue";
import GameBoard from "../components/GameBoard.vue";
import HistoryList from "../components/HistoryList.vue";
import type { AiLevel, AiMoveResponse, GameState } from "../types/game";

const gameState = ref<GameState | null>(null);
const aiResponse = ref<AiMoveResponse | null>(null);
const loading = ref(false);
const aiLoading = ref(false);
const autoReplyTimer = ref<number | null>(null);
const errorMessage = ref("");
const aiLevel = ref<AiLevel>("medium");
const autoReply = ref(false);
const showCellNumbers = ref(true);
const showLegalMoves = ref(true);
const showWinningMoves = ref(true);
const showThreatMoves = ref(true);
const showRemovalPreview = ref(true);

const canUndo = computed(() => Boolean(gameState.value && gameState.value.history.length > 0));
const waitingForAutoReply = computed(() => autoReplyTimer.value !== null);
const isBusy = computed(() => loading.value || aiLoading.value || waitingForAutoReply.value);
const canUseAi = computed(() => Boolean(gameState.value && gameState.value.status === "playing"));

function clearAutoReplyTimer() {
  if (autoReplyTimer.value !== null) {
    window.clearTimeout(autoReplyTimer.value);
    autoReplyTimer.value = null;
  }
}

async function runStateAction(action: () => Promise<GameState>): Promise<GameState | null> {
  clearAutoReplyTimer();
  loading.value = true;
  errorMessage.value = "";
  try {
    const state = await action();
    gameState.value = state;
    aiResponse.value = null;
    return state;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "操作失败。";
    return null;
  } finally {
    loading.value = false;
  }
}

function startNewGame() {
  void runStateAction(() => createGame());
}

function undoMove() {
  if (!gameState.value || isBusy.value) {
    return;
  }
  const gameId = gameState.value.game_id;
  void runStateAction(() => undo(gameId));
}

async function placeAt(position: number) {
  if (!gameState.value || gameState.value.status !== "playing" || isBusy.value) {
    return;
  }
  const gameId = gameState.value.game_id;
  const state = await runStateAction(() => makeMove(gameId, position));
  if (state && autoReply.value && state.status === "playing") {
    scheduleAutoReply();
  }
}

function scheduleAutoReply() {
  clearAutoReplyTimer();
  autoReplyTimer.value = window.setTimeout(() => {
    autoReplyTimer.value = null;
    void runAiMove();
  }, 500);
}

async function showHint() {
  if (!gameState.value || !canUseAi.value || isBusy.value) {
    return;
  }
  const gameId = gameState.value.game_id;
  aiLoading.value = true;
  errorMessage.value = "";
  try {
    const response = await getHint(gameId, aiLevel.value);
    aiResponse.value = response;
    gameState.value = response.state;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "AI 推荐失败。";
  } finally {
    aiLoading.value = false;
  }
}

async function runAiMove() {
  if (!gameState.value || !canUseAi.value || aiLoading.value || loading.value) {
    return;
  }
  clearAutoReplyTimer();
  const gameId = gameState.value.game_id;
  aiLoading.value = true;
  errorMessage.value = "";
  try {
    const response = await makeAiMove(gameId, {
      level: aiLevel.value,
      seed: null,
      auto_apply: true,
    });
    aiResponse.value = response;
    gameState.value = response.state;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "AI 落子失败。";
  } finally {
    aiLoading.value = false;
  }
}

function updateAutoReply(value: boolean) {
  autoReply.value = value;
  if (!value) {
    clearAutoReplyTimer();
  }
}

onMounted(() => {
  startNewGame();
});

onBeforeUnmount(() => {
  clearAutoReplyTimer();
});
</script>

<template>
  <header class="app-header">
    <div class="title-block">
      <h1 class="app-title">月亮棋 · 银月茶会</h1>
      <p class="subtitle">入席执棋，与银月对弈；若想取胜，先看清哪颗月亮将要落下。</p>
    </div>
    <div v-if="gameState" class="status-pill" :class="`status-${gameState.status}`">
      <span v-if="gameState.status === 'playing'">轮到 {{ gameState.current_player }}</span>
      <span v-else-if="gameState.status === 'won'">{{ gameState.winner }} 获胜</span>
      <span v-else>平局</span>
    </div>
  </header>

  <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

  <section v-if="gameState" class="ai-main-layout">
    <GameBoard
      :state="gameState"
      :show-cell-numbers="showCellNumbers"
      :show-legal-moves="showLegalMoves"
      :show-winning-moves="showWinningMoves"
      :show-threat-moves="showThreatMoves"
      :show-removal-preview="showRemovalPreview"
      :disabled="isBusy"
      @place="placeAt"
    />

    <div class="ai-side-stack">
      <AnalysisPanel :state="gameState" />
      <AiPanel
        :level="aiLevel"
        :auto-reply="autoReply"
        :loading="isBusy"
        :disabled="!canUseAi"
        :response="aiResponse"
        @hint="showHint"
        @ai-move="runAiMove"
        @update:level="aiLevel = $event"
        @update:auto-reply="updateAutoReply"
      />
    </div>
  </section>

  <section v-if="gameState" class="bottom-layout">
    <ControlPanel
      :loading="isBusy"
      :can-undo="canUndo"
      :show-cell-numbers="showCellNumbers"
      :show-legal-moves="showLegalMoves"
      :show-winning-moves="showWinningMoves"
      :show-threat-moves="showThreatMoves"
      :show-removal-preview="showRemovalPreview"
      @new-game="startNewGame"
      @undo="undoMove"
      @update:show-cell-numbers="showCellNumbers = $event"
      @update:show-legal-moves="showLegalMoves = $event"
      @update:show-winning-moves="showWinningMoves = $event"
      @update:show-threat-moves="showThreatMoves = $event"
      @update:show-removal-preview="showRemovalPreview = $event"
    />

    <HistoryList :history="gameState.history" />
  </section>

  <section v-else class="loading-panel">正在连接后端...</section>
</template>
