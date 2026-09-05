<script setup lang="ts">
import type { Piece } from "../types/game";
import { useI18n } from "vue-i18n";

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
  isLastMove?: boolean;
}>();

const emit = defineEmits<{
  place: [position: number];
}>();
const { t } = useI18n();

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
  const labels = [props.piece ? t("game.cellWithPiece", { position: props.position, piece: props.pieceDescription ?? props.piece.id }) : t("game.position", { position: props.position })];
  if (props.showLegalHighlight) labels.push(t("game.legal"));
  if (props.isCurrentWinningMove) labels.push(t("game.winning"));
  if (props.isOpponentRealThreat) labels.push(t("game.threat"));
  if (props.isPendingRemoval) labels.push(t("ux.removing"));
  if (props.isLastMove) labels.push(t("ux.lastMove"));
  return labels.join("; ");
}
</script>

<template>
  <button
    class="game-cell"
    :class="[
      pieceClassName(),
      {
        'has-piece': piece,
        'last-move': isLastMove,
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
    <span v-if="isPendingRemoval" class="removal-badge" aria-hidden="true">{{ t("ux.removing") }}</span>
    <span v-if="piece" class="piece-label">{{ pieceText() }}</span>
    <span
      v-if="showLegalHighlight || isCurrentWinningMove || isOpponentRealThreat"
      class="cell-hints"
      aria-hidden="true"
    >
      <span v-if="showLegalHighlight" class="cell-hint hint-legal">•</span>
      <span v-if="isCurrentWinningMove" class="cell-hint hint-win">◆ {{ t('game.winning') }}</span>
      <span v-if="isOpponentRealThreat" class="cell-hint hint-threat">▲ {{ t('game.threat') }}</span>
    </span>
  </button>
</template>
