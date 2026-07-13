<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import type { PlayerDisplayMap } from "../../types/display";
import type { GameState } from "../../types/game";
import { formatPieceFull, formatPlayer } from "../../utils/playerDisplay";

const props = withDefaults(
  defineProps<{
    state: GameState;
    displayMap: PlayerDisplayMap;
    showRemovalPreview: boolean;
    aiThinking?: boolean;
    thinkingText?: string;
    title?: string;
  }>(),
  {
    aiThinking: false,
    thinkingText: "",
    title: "",
  },
);
const { t } = useI18n();

const currentActionText = computed(() => {
  return formatPlayer(props.state.current_player, props.displayMap);
});

const cardTitle = computed(() => (props.state.status === "playing" ? (props.title || t("game.status")) : t("game.ended")));

const resultText = computed(() => {
  if (props.state.status === "won") {
    return t("game.winner", { player: formatPlayer(props.state.winner, props.displayMap, t("common.none")) });
  }
  if (props.state.status === "draw") {
    return t("game.draw");
  }
  return t("game.playing");
});

const legalMovesText = computed(() => (props.state.legal_moves.length > 0 ? props.state.legal_moves.join(", ") : t("common.none")));
const winningLineText = computed(() =>
  props.state.winning_line && props.state.winning_line.length > 0 ? props.state.winning_line.join(", ") : t("common.none"),
);
</script>

<template>
  <section class="game-status-card" :class="{ 'has-result': state.status !== 'playing' }" :aria-label="t('game.status')">
    <div class="section-title">
      <span>{{ cardTitle }}</span>
      <strong>{{ t('common.move', { count: state.move_number }) }}</strong>
    </div>

    <dl v-if="state.status === 'playing'" class="game-status-grid">
      <div>
        <dt>{{ t('game.currentPlayer') }}</dt>
        <dd>{{ currentActionText }}</dd>
      </div>
      <div v-if="aiThinking">
        <dt>{{ t('game.actionStatus') }}</dt>
        <dd>{{ thinkingText }}</dd>
      </div>
      <div>
        <dt>{{ t('game.pending') }}</dt><dd>{{ showRemovalPreview ? formatPieceFull(state.pending_removal, displayMap, t('common.none')) : t('common.hidden') }}</dd>
      </div>
      <div>
        <dt>{{ t('game.upcoming') }}</dt><dd>{{ showRemovalPreview ? formatPieceFull(state.upcoming_removal, displayMap, t('common.none')) : t('common.hidden') }}</dd>
      </div>
      <div>
        <dt>{{ t('game.legalMoves') }}</dt>
        <dd>{{ legalMovesText }}</dd>
      </div>
    </dl>

    <section
      v-if="state.status !== 'playing'"
      class="result-banner game-result"
      :class="state.status === 'won' ? 'result-win' : 'result-draw'"
      :aria-label="t('game.result')"
    >
      <span class="result-kicker">{{ t('game.result') }}</span>
      <strong>{{ resultText }}</strong>
      <p v-if="state.status === 'won'">{{ t('game.winningLine', { moves: winningLineText }) }}</p>
      <p v-else>{{ t('game.drawAfter', { count: state.move_number }) }}</p>
    </section>
  </section>
</template>
