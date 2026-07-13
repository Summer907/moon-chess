<script setup lang="ts">
import { computed } from "vue";
import type { AiLevel, AiMoveResponse, AiOutcome } from "../types/game";
import { useI18n } from "vue-i18n";

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

const { t } = useI18n();
const levels = computed((): Array<{ value: AiLevel; label: string }> => [
  { value: "easy", label: t("difficulty.easy") }, { value: "medium", label: t("difficulty.medium") }, { value: "hard", label: t("difficulty.hard") },
]);
function reasonText(reason: { code: string; params: Record<string, unknown> }): string { return t(`ai.${reason.code}`, reason.params); }

function levelLabel(level: AiLevel): string {
  return levels.value.find((item) => item.value === level)?.label ?? level;
}

function outcomeLabel(outcome: AiOutcome): string {
  const labels: Record<AiOutcome, string> = {
    win: t("ai.win"), draw: t("game.draw"), loss: t("ai.loss"), unknown: t("ai.unknown"),
  };
  return labels[outcome];
}

function scoreText(score: number | null): string {
  return score === null ? t("common.none") : score.toFixed(1);
}

function pliesText(plies: number | null): string {
  return plies === null ? t("common.none") : t("common.move", { count: plies });
}
</script>

<template>
  <section class="ai-panel" :aria-label="t('ai.panel')">
    <div class="section-title">
      <span>{{ t('ai.title') }}</span>
      <strong>{{ response ? levelLabel(response.level) : levelLabel(level) }}</strong>
    </div>

    <div class="ai-controls">
      <label class="select-row">
        <span>{{ t('ai.difficulty') }}</span>
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
        <button type="button" :disabled="loading || disabled" @click="$emit('hint')">{{ t('ai.hint') }}</button>
        <button type="button" :disabled="loading || disabled" @click="$emit('aiMove')">{{ t('ai.move') }}</button>
      </div>

      <label class="toggle-row">
        <input
          type="checkbox"
          :checked="autoReply"
          :disabled="loading"
          @change="$emit('update:autoReply', ($event.target as HTMLInputElement).checked)"
        />
        <span>{{ t('ai.autoReply') }}</span>
      </label>
    </div>

    <section v-if="response" class="ai-response" :aria-label="t('ai.explanation')">
      <dl class="ai-summary">
        <div>
          <dt>{{ response.applied ? t('ai.actual') : t('ai.recommended') }}</dt>
          <dd>{{ response.move }}</dd>
        </div>
        <div>
          <dt>{{ t('ai.outcome') }}</dt>
          <dd>{{ outcomeLabel(response.outcome) }}</dd>
        </div>
        <div>
          <dt>{{ t('ai.confidence') }}</dt>
          <dd>{{ response.confidence }}</dd>
        </div>
      </dl>

      <ul class="ai-reason-list">
        <li v-for="(reason, index) in response.reason_codes" :key="`${reason.code}-${index}`">{{ reasonText(reason) }}</li>
      </ul>

      <div class="evaluation-table" :aria-label="t('ai.candidates')">
        <div class="evaluation-header">
          <span>{{ t('ai.point') }}</span><span>{{ t('ai.result') }}</span><span>{{ t('ai.score') }}</span><span>{{ t('ai.distance') }}</span><span>{{ t('ai.reason') }}</span>
        </div>
        <div v-for="item in response.evaluated_moves" :key="item.move" class="evaluation-row">
          <strong>{{ item.move }}</strong>
          <span>{{ outcomeLabel(item.outcome) }}</span>
          <span>{{ scoreText(item.score) }}</span>
          <span>{{ pliesText(item.plies) }}</span>
          <span>{{ item.reason_codes.map(reasonText).join(' ') }}</span>
        </div>
      </div>
    </section>

    <p v-else class="empty-text">{{ t('ai.empty') }}</p>
  </section>
</template>
