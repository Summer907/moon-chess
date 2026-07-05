<script setup lang="ts">
import { computed } from "vue";

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
    thinkingText: "哥伦比娅思考中……",
    title: "当前状态",
  },
);

const currentActionText = computed(() => {
  if (props.state.status === "won") {
    return `${formatPlayer(props.state.winner, props.displayMap)}胜利`;
  }
  if (props.state.status === "draw") {
    return "平局";
  }
  if (props.aiThinking) {
    return props.thinkingText;
  }
  return formatPlayer(props.state.current_player, props.displayMap);
});

const resultText = computed(() => {
  if (props.state.status === "won") {
    return `${formatPlayer(props.state.winner, props.displayMap)}胜利`;
  }
  if (props.state.status === "draw") {
    return "平局";
  }
  return "对弈中";
});

const legalMovesText = computed(() => (props.state.legal_moves.length > 0 ? props.state.legal_moves.join("、") : "无"));
const winningLineText = computed(() =>
  props.state.winning_line && props.state.winning_line.length > 0 ? props.state.winning_line.join("、") : "无",
);
</script>

<template>
  <section class="game-status-card" :class="{ 'has-result': state.status !== 'playing' }" aria-label="当前状态">
    <div class="section-title">
      <span>{{ title }}</span>
      <strong>第 {{ state.move_number }} 手</strong>
    </div>

    <dl class="game-status-grid">
      <div>
        <dt>当前行动方</dt>
        <dd>{{ currentActionText }}</dd>
      </div>
      <div>
        <dt>本手先消</dt>
        <dd>{{ showRemovalPreview ? formatPieceFull(state.pending_removal, displayMap) : "已隐藏" }}</dd>
      </div>
      <div>
        <dt>下回预告</dt>
        <dd>{{ showRemovalPreview ? formatPieceFull(state.upcoming_removal, displayMap) : "已隐藏" }}</dd>
      </div>
      <div>
        <dt>合法落点</dt>
        <dd>{{ legalMovesText }}</dd>
      </div>
    </dl>

    <section
      v-if="state.status !== 'playing'"
      class="result-banner game-result"
      :class="state.status === 'won' ? 'result-win' : 'result-draw'"
      aria-label="对局结果"
    >
      <span class="result-kicker">对局结果</span>
      <strong>{{ resultText }}</strong>
      <p v-if="state.status === 'won'">胜线：{{ winningLineText }}</p>
      <p v-else>第 {{ state.move_number }} 手后，判定为平局。</p>
    </section>
  </section>
</template>
