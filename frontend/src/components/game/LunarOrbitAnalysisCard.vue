<script setup lang="ts">
import type { PlayerDisplayMap } from "../../types/display";
import type { GameState, Piece, Player } from "../../types/game";
import { formatPieceFull, formatPieceShort, formatPlayer } from "../../utils/playerDisplay";
import { useI18n } from "vue-i18n";

defineProps<{
  state: GameState;
  displayMap: PlayerDisplayMap;
}>();
const { t } = useI18n();

function numberList(values: number[]): string {
  return values.length > 0 ? values.join(", ") : t("common.none");
}

function pieceList(values: Piece[], displayMap: PlayerDisplayMap): string {
  return values.length > 0 ? values.map((piece) => formatPieceFull(piece, displayMap, t("common.none"))).join(", ") : t("common.none");
}

function formatAnalysisLine(line: string, displayMap: PlayerDisplayMap): string {
  return line
    .replace(/([XO])(\d+)/g, (_, player: Player, order: string) => {
      return `${formatPlayer(player, displayMap)}${formatPieceShort({
        id: `${player}${order}`,
        player,
        order: Number(order),
        position: 0,
      })}`;
    })
    .replace(/(^|[^\w])([XO])(?=$|[^\w])/g, (_, prefix: string, player: Player) => {
      return `${prefix}${formatPlayer(player, displayMap)}`;
    });
}
</script>

<template>
  <section class="game-analysis-card" :aria-label="t('analysis.title')">
    <div class="section-title">
      <span>{{ t('analysis.title') }}</span><strong>{{ t('analysis.backend') }}</strong>
    </div>

    <dl class="analysis-grid">
      <div>
        <dt>{{ t('game.retained') }}</dt>
        <dd>{{ pieceList(state.analysis.retained_pieces_after_removal, displayMap) }}</dd>
      </div>
      <div>
        <dt>{{ t('game.directWins') }}</dt>
        <dd>{{ numberList(state.analysis.current_winning_moves) }}</dd>
      </div>
      <div>
        <dt>{{ t('game.realThreats') }}</dt>
        <dd>{{ numberList(state.analysis.opponent_real_threats) }}</dd>
      </div>
    </dl>

    <ul class="explanation-list">
      <li v-if="state.status === 'won'">{{ t('game.wonAnalysis', { player: formatPlayer(state.winner, displayMap, t('common.none')) }) }}</li>
      <li v-else-if="state.status === 'draw'">{{ t('game.drawAnalysis') }}</li>
      <template v-else>
        <li>{{ state.pending_removal ? t('game.pendingRemoval', { piece: formatPieceFull(state.pending_removal, displayMap, t('common.none')) }) : t('game.noOwnRemoval') }}</li>
        <li>{{ state.upcoming_removal ? t('game.nextRemoval', { piece: formatPieceFull(state.upcoming_removal, displayMap, t('common.none')) }) : t('game.noNextRemoval') }}</li>
      </template>
    </ul>
  </section>
</template>
