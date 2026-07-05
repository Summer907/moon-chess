<script setup lang="ts">
import type { PlayerDisplayMap } from "../../types/display";
import type { GameState, Piece, Player } from "../../types/game";
import { formatPieceFull, formatPieceShort, formatPlayer } from "../../utils/playerDisplay";

defineProps<{
  state: GameState;
  displayMap: PlayerDisplayMap;
}>();

function numberList(values: number[]): string {
  return values.length > 0 ? values.join("、") : "无";
}

function pieceList(values: Piece[], displayMap: PlayerDisplayMap): string {
  return values.length > 0 ? values.map((piece) => formatPieceFull(piece, displayMap)).join("、") : "无";
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
  <section class="game-analysis-card" aria-label="推演详情">
    <div class="section-title">
      <span>推演详情</span>
      <strong>后端判定</strong>
    </div>

    <dl class="analysis-grid">
      <div>
        <dt>消子后保留</dt>
        <dd>{{ pieceList(state.analysis.retained_pieces_after_removal, displayMap) }}</dd>
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

    <ul v-if="state.analysis.explanation.length > 0" class="explanation-list">
      <li v-for="(line, index) in state.analysis.explanation" :key="`${index}-${line}`">
        {{ formatAnalysisLine(line, displayMap) }}
      </li>
    </ul>
    <p v-else class="empty-text">暂无推演说明。</p>
  </section>
</template>
