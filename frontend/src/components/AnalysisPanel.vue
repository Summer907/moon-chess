<script setup lang="ts">
import type { GameState, Piece } from "../types/game";

defineProps<{
  state: GameState;
}>();

function pieceText(piece: Piece | null): string {
  return piece ? `${piece.id}（位置 ${piece.position}）` : "无";
}

function numberList(values: number[]): string {
  return values.length > 0 ? values.join("、") : "无";
}

function pieceList(values: Piece[]): string {
  return values.length > 0 ? values.map((piece) => piece.id).join("、") : "无";
}

function lineText(values: number[] | null): string {
  return values && values.length > 0 ? values.join("、") : "无";
}
</script>

<template>
  <aside class="analysis-panel" :class="{ 'has-result': state.status !== 'playing' }" aria-label="局面说明">
    <div class="section-title">
      <span>局面说明</span>
      <strong>第 {{ state.move_number }} 手</strong>
    </div>

    <dl class="analysis-grid">
      <div>
        <dt>当前行动方</dt>
        <dd>{{ state.analysis.current_player }}</dd>
      </div>
      <div>
        <dt>本手先消</dt>
        <dd>{{ pieceText(state.analysis.pending_removal) }}</dd>
      </div>
      <div>
        <dt>本手后预告</dt>
        <dd>{{ pieceText(state.analysis.upcoming_removal) }}</dd>
      </div>
      <div>
        <dt>消子后保留</dt>
        <dd>{{ pieceList(state.analysis.retained_pieces_after_removal) }}</dd>
      </div>
      <div>
        <dt>合法落子</dt>
        <dd>{{ numberList(state.legal_moves) }}</dd>
      </div>
      <div>
        <dt>当前方直接胜点</dt>
        <dd>{{ numberList(state.analysis.current_winning_moves) }}</dd>
      </div>
      <div>
        <dt>对手真实威胁</dt>
        <dd>{{ numberList(state.analysis.opponent_real_threats) }}</dd>
      </div>
    </dl>

    <ul class="explanation-list">
      <li v-for="line in state.analysis.explanation" :key="line">{{ line }}</li>
    </ul>

    <section
      v-if="state.status !== 'playing'"
      class="result-banner"
      :class="state.status === 'won' ? 'result-win' : 'result-draw'"
      aria-label="对局结果"
    >
      <span class="result-kicker">对局结果</span>
      <strong v-if="state.status === 'won'">{{ state.winner }} 获胜</strong>
      <strong v-else>平局</strong>
      <p v-if="state.status === 'won'">胜线：{{ lineText(state.winning_line) }}</p>
      <p v-else>第 {{ state.move_number }} 手后，后端判定为平局。</p>
    </section>
  </aside>
</template>
