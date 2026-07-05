<script setup lang="ts">
import type { AiLevel, AiMoveResponse, AiOutcome } from "../types/game";

defineProps<{
  level: AiLevel;
  autoReply: boolean;
  loading: boolean;
  disabled: boolean;
  response: AiMoveResponse | null;
}>();

defineEmits<{
  hint: [];
  aiMove: [];
  "update:level": [value: AiLevel];
  "update:autoReply": [value: boolean];
}>();

const levels: Array<{ value: AiLevel; label: string }> = [
  { value: "easy", label: "虹月 · 简单" },
  { value: "medium", label: "恒月 · 中等" },
  { value: "hard", label: "霜月 · 困难" },
];

function levelLabel(level: AiLevel): string {
  return levels.find((item) => item.value === level)?.label ?? level;
}

function outcomeLabel(outcome: AiOutcome): string {
  const labels: Record<AiOutcome, string> = {
    win: "胜",
    draw: "和棋",
    loss: "负",
    unknown: "未知",
  };
  return labels[outcome];
}

function scoreText(score: number | null): string {
  return score === null ? "无" : score.toFixed(1);
}

function pliesText(plies: number | null): string {
  return plies === null ? "无" : `${plies} 手`;
}
</script>

<template>
  <section class="ai-panel" aria-label="AI 控制区">
    <div class="section-title">
      <span>规则 AI</span>
      <strong>{{ response ? levelLabel(response.level) : levelLabel(level) }}</strong>
    </div>

    <div class="ai-controls">
      <label class="select-row">
        <span>难度</span>
        <select
          :value="level"
          :disabled="loading"
          @change="$emit('update:level', ($event.target as HTMLSelectElement).value as AiLevel)"
        >
          <option v-for="item in levels" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </label>

      <div class="button-row">
        <button type="button" :disabled="loading || disabled" @click="$emit('hint')">查看推荐</button>
        <button type="button" :disabled="loading || disabled" @click="$emit('aiMove')">AI 落子</button>
      </div>

      <label class="toggle-row">
        <input
          type="checkbox"
          :checked="autoReply"
          :disabled="loading"
          @change="$emit('update:autoReply', ($event.target as HTMLInputElement).checked)"
        />
        <span>AI 自动回应</span>
      </label>
    </div>

    <section v-if="response" class="ai-response" aria-label="AI 说明区">
      <dl class="ai-summary">
        <div>
          <dt>{{ response.applied ? "实际落子" : "推荐落子" }}</dt>
          <dd>{{ response.move }}</dd>
        </div>
        <div>
          <dt>理论结果</dt>
          <dd>{{ outcomeLabel(response.outcome) }}</dd>
        </div>
        <div>
          <dt>判断方式</dt>
          <dd>{{ response.confidence }}</dd>
        </div>
      </dl>

      <ul class="ai-reason-list">
        <li v-for="line in response.reason" :key="line">{{ line }}</li>
      </ul>

      <div class="evaluation-table" aria-label="候选落子评估">
        <div class="evaluation-header">
          <span>点位</span>
          <span>结果</span>
          <span>分数</span>
          <span>距离</span>
          <span>理由</span>
        </div>
        <div v-for="item in response.evaluated_moves" :key="item.move" class="evaluation-row">
          <strong>{{ item.move }}</strong>
          <span>{{ outcomeLabel(item.outcome) }}</span>
          <span>{{ scoreText(item.score) }}</span>
          <span>{{ pliesText(item.plies) }}</span>
          <span>{{ item.reason }}</span>
        </div>
      </div>
    </section>

    <p v-else class="empty-text">尚未生成 AI 说明。</p>
  </section>
</template>
