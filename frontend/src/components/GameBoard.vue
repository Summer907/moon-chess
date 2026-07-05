<script setup lang="ts">
import { computed } from "vue";

import GameCell from "./GameCell.vue";
import type { GameState, Piece } from "../types/game";

const props = defineProps<{
  state: GameState;
  showCellNumbers: boolean;
  showLegalMoves: boolean;
  showWinningMoves: boolean;
  showThreatMoves: boolean;
  showRemovalPreview: boolean;
  disabled: boolean;
}>();

const emit = defineEmits<{
  place: [position: number];
}>();

const positions = [1, 2, 3, 4, 5, 6, 7, 8, 9];
const removalPreview = computed(() => props.state.pending_removal ?? props.state.upcoming_removal);

function pieceAt(position: number): Piece | null {
  return props.state.board[position - 1] ?? null;
}

function isPendingRemoval(piece: Piece | null): boolean {
  return Boolean(props.showRemovalPreview && piece && removalPreview.value?.id === piece.id);
}

function isWinningPosition(position: number): boolean {
  return props.state.winning_line?.includes(position) ?? false;
}

function isLegalMove(position: number): boolean {
  return props.state.status === "playing" && props.state.legal_moves.includes(position);
}

function shouldHighlightLegalMove(position: number): boolean {
  return props.showLegalMoves && isLegalMove(position);
}

function isCurrentWinningMove(position: number): boolean {
  return props.showWinningMoves && props.state.analysis.current_winning_moves.includes(position);
}

function isOpponentRealThreat(position: number): boolean {
  return props.showThreatMoves && props.state.analysis.opponent_real_threats.includes(position);
}
</script>

<template>
  <section class="board-panel" aria-label="月亮棋棋盘">
    <div class="board-meta">
      <div>
        <span>第 {{ state.move_number }} 手后</span>
        <strong>当前：{{ state.current_player }}</strong>
      </div>
      <div class="pending-text">
        消失预告：
        <strong>{{ showRemovalPreview ? (removalPreview ? removalPreview.id : "无") : "已隐藏" }}</strong>
      </div>
    </div>

    <div class="board-grid">
      <GameCell
        v-for="position in positions"
        :key="position"
        :position="position"
        :piece="pieceAt(position)"
        :show-number="showCellNumbers"
        :is-pending-removal="isPendingRemoval(pieceAt(position))"
        :is-winning="isWinningPosition(position)"
        :is-legal="isLegalMove(position)"
        :show-legal-highlight="shouldHighlightLegalMove(position)"
        :is-current-winning-move="isCurrentWinningMove(position)"
        :is-opponent-real-threat="isOpponentRealThreat(position)"
        :disabled="disabled"
        @place="emit('place', $event)"
      />
    </div>
  </section>
</template>
