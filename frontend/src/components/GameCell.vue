<script setup lang="ts">
import type { Piece } from "../types/game";

const props = defineProps<{
  position: number;
  piece: Piece | null;
  pieceLabel?: string;
  pieceDescription?: string;
  pieceClass?: string;
  showNumber: boolean;
  isPendingRemoval: boolean;
  isWinning: boolean;
  isLegal: boolean;
  showLegalHighlight: boolean;
  isCurrentWinningMove: boolean;
  isOpponentRealThreat: boolean;
  disabled: boolean;
}>();

const emit = defineEmits<{
  place: [position: number];
}>();

function handleClick() {
  if (!props.disabled && props.isLegal) {
    emit("place", props.position);
  }
}

function pieceClassName(): string | undefined {
  if (!props.piece) {
    return undefined;
  }
  return props.pieceClass ?? `piece-${props.piece.player}`;
}

function pieceText(): string {
  if (!props.piece) {
    return "";
  }
  return props.pieceLabel ?? props.piece.id;
}

function ariaLabel(): string {
  const piecePart = props.piece ? `，${props.pieceDescription ?? props.piece.id}` : "";
  return `位置 ${props.position}${piecePart}`;
}
</script>

<template>
  <button
    class="game-cell"
    :class="[
      pieceClassName(),
      {
        'has-piece': piece,
        'pending-removal': isPendingRemoval,
        winning: isWinning,
        legal: isLegal,
        'legal-highlight': showLegalHighlight,
        'direct-win-highlight': isCurrentWinningMove,
        'real-threat-highlight': isOpponentRealThreat,
      },
    ]"
    type="button"
    :disabled="disabled || !isLegal"
    :aria-label="ariaLabel()"
    @click="handleClick"
  >
    <span v-if="showNumber" class="cell-number">{{ position }}</span>
    <span v-if="piece" class="piece-label">{{ pieceText() }}</span>
    <span
      v-if="showLegalHighlight || isCurrentWinningMove || isOpponentRealThreat"
      class="cell-hints"
      aria-hidden="true"
    >
      <span v-if="showLegalHighlight" class="cell-hint hint-legal">可下</span>
      <span v-if="isCurrentWinningMove" class="cell-hint hint-win">胜点</span>
      <span v-if="isOpponentRealThreat" class="cell-hint hint-threat">威胁</span>
    </span>
  </button>
</template>
