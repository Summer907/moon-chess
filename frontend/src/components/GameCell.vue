<script setup lang="ts">
import type { Piece } from "../types/game";

const props = defineProps<{
  position: number;
  piece: Piece | null;
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
</script>

<template>
  <button
    class="game-cell"
    :class="{
      'has-piece': piece,
      [`piece-${piece?.player}`]: piece,
      'pending-removal': isPendingRemoval,
      winning: isWinning,
      legal: isLegal,
      'legal-highlight': showLegalHighlight,
      'direct-win-highlight': isCurrentWinningMove,
      'real-threat-highlight': isOpponentRealThreat,
    }"
    type="button"
    :disabled="disabled || !isLegal"
    :aria-label="`位置 ${position}${piece ? `，${piece.id}` : ''}`"
    @click="handleClick"
  >
    <span v-if="showNumber" class="cell-number">{{ position }}</span>
    <span v-if="piece" class="piece-label">{{ piece.id }}</span>
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
