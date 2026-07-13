<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

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
  formatPieceLabel?: (piece: Piece) => string;
  formatPieceDescription?: (piece: Piece) => string;
  pieceClass?: (piece: Piece) => string;
}>();

const emit = defineEmits<{
  place: [position: number];
}>();
const { t } = useI18n();

const positions = [1, 2, 3, 4, 5, 6, 7, 8, 9];
const removalPreview = computed(() => props.state.pending_removal ?? props.state.upcoming_removal);
const winningLine = computed(() => {
  const [start, , end] = props.state.winning_line ?? [];
  if (!start || !end) {
    return null;
  }

  return {
    x1: ((start - 1) % 3 + 0.5) * 100,
    y1: (Math.floor((start - 1) / 3) + 0.5) * 100,
    x2: ((end - 1) % 3 + 0.5) * 100,
    y2: (Math.floor((end - 1) / 3) + 0.5) * 100,
  };
});

function pieceAt(position: number): Piece | null {
  return props.state.board[position - 1] ?? null;
}

function pieceLabel(piece: Piece | null): string | undefined {
  if (!piece) {
    return undefined;
  }
  return props.formatPieceLabel?.(piece) ?? piece.id;
}

function pieceDescription(piece: Piece | null): string | undefined {
  if (!piece) {
    return undefined;
  }
  return props.formatPieceDescription?.(piece) ?? piece.id;
}

function pieceClassName(piece: Piece | null): string | undefined {
  if (!piece) {
    return undefined;
  }
  return props.pieceClass?.(piece) ?? `piece-${piece.player}`;
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
  <section class="board-panel" :aria-label="t('game.board')">
    <div class="board-meta">
      <div>
        <span>{{ t('common.afterMove', { count: state.move_number }) }}</span>
        <strong v-if="state.status !== 'playing'">{{ t('game.ended') }}</strong>
      </div>
      <div v-if="state.status === 'playing'" class="pending-text">
        {{ t('game.preview') }}
        <strong>{{ showRemovalPreview ? (removalPreview ? pieceDescription(removalPreview) : t('common.none')) : t('common.hidden') }}</strong>
      </div>
    </div>

    <div class="board-stage">
      <div class="board-aura" aria-hidden="true"></div>
      <div class="board-ornaments" aria-hidden="true">
        <span class="board-ornament board-ornament--top"></span>
        <span class="board-ornament board-ornament--right"></span>
        <span class="board-ornament board-ornament--bottom"></span>
        <span class="board-ornament board-ornament--left"></span>
      </div>
      <div class="board-grid" :class="{ 'has-winner': winningLine }">
        <svg v-if="winningLine" class="winning-line" viewBox="0 0 300 300" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <filter id="winning-line-glow" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <line
            :x1="winningLine.x1"
            :y1="winningLine.y1"
            :x2="winningLine.x2"
            :y2="winningLine.y2"
            pathLength="1"
          />
        </svg>
        <GameCell
          v-for="position in positions"
          :key="position"
          :position="position"
          :piece="pieceAt(position)"
          :piece-label="pieceLabel(pieceAt(position))"
          :piece-description="pieceDescription(pieceAt(position))"
          :piece-class="pieceClassName(pieceAt(position))"
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
    </div>
  </section>
</template>
