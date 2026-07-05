<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { createGame, makeMove, undo } from "./api/client";
import AnalysisPanel from "./components/AnalysisPanel.vue";
import ControlPanel from "./components/ControlPanel.vue";
import GameBoard from "./components/GameBoard.vue";
import HistoryList from "./components/HistoryList.vue";
import type { GameState } from "./types/game";

const gameState = ref<GameState | null>(null);
const loading = ref(false);
const errorMessage = ref("");
const showCellNumbers = ref(true);
const showLegalMoves = ref(true);
const showWinningMoves = ref(true);
const showThreatMoves = ref(true);
const showRemovalPreview = ref(true);

const canUndo = computed(() => Boolean(gameState.value && gameState.value.history.length > 0));

async function runAction(action: () => Promise<GameState>) {
  loading.value = true;
  errorMessage.value = "";
  try {
    gameState.value = await action();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "操作失败。";
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

onMounted(() => {
  startNewGame();
});
</script>

<template>
  <main class="app-shell">
    <header class="app-header">
      <div class="title-block">
        <h1 class="app-title">月亮棋 · 模拟器</h1>
        <p class="subtitle">三是表象，四是本征；七，是二者交叠后的垂直超越之径。</p>
      </div>
      <div v-if="gameState" class="status-pill" :class="`status-${gameState.status}`">
        <span v-if="gameState.status === 'playing'">轮到 {{ gameState.current_player }}</span>
        <span v-else-if="gameState.status === 'won'">{{ gameState.winner }} 获胜</span>
        <span v-else>平局</span>
      </div>
    </header>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <section v-if="gameState" class="main-layout">
      <GameBoard
        :state="gameState"
        :show-cell-numbers="showCellNumbers"
        :show-legal-moves="showLegalMoves"
        :show-winning-moves="showWinningMoves"
        :show-threat-moves="showThreatMoves"
        :show-removal-preview="showRemovalPreview"
        :disabled="loading"
        @place="placeAt"
      />

      <AnalysisPanel :state="gameState" />
    </section>

    <section v-if="gameState" class="bottom-layout">
      <ControlPanel
        :loading="loading"
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
  </main>
</template>
