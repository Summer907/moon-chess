<script setup lang="ts">
import type { TravelerSide } from "../../types/display";
import type { AiLevel } from "../../types/game";

withDefaults(
  defineProps<{
    travelerSide: TravelerSide;
    loading: boolean;
    canUndo: boolean;
    showCellNumbers: boolean;
    showLegalMoves: boolean;
    showWinningMoves: boolean;
    showThreatMoves: boolean;
    showRemovalPreview: boolean;
    aiLevel?: AiLevel;
    showAiLevel?: boolean;
    title?: string;
    newGameLabel?: string;
    newGameTitle?: string;
    undoLabel?: string;
    undoTitle?: string;
  }>(),
  {
    showAiLevel: true,
    title: "对弈配置",
    newGameLabel: "再启银月",
    newGameTitle: "清空当前棋局，重新开始一场银月茶会。",
    undoLabel: "逆转月轨",
    undoTitle: "沿月影回溯，撤回上一轮对弈。",
  },
);

defineEmits<{
  newGame: [];
  undo: [];
  "update:travelerSide": [value: TravelerSide];
  "update:aiLevel": [value: AiLevel];
  "update:showCellNumbers": [value: boolean];
  "update:showLegalMoves": [value: boolean];
  "update:showWinningMoves": [value: boolean];
  "update:showThreatMoves": [value: boolean];
  "update:showRemovalPreview": [value: boolean];
}>();

const sideOptions: Array<{ value: TravelerSide; label: string }> = [
  { value: "first", label: "旅行者先手" },
  { value: "second", label: "旅行者后手" },
];

const levelOptions: Array<{ value: AiLevel; label: string }> = [
  { value: "easy", label: "虹月 · 简单" },
  { value: "medium", label: "恒月 · 中等" },
  { value: "hard", label: "霜月 · 困难" },
];
</script>

<template>
  <section class="game-settings-card" aria-label="配置">
    <div class="section-title">
      <span>{{ title }}</span>
    </div>

    <fieldset class="settings-field">
      <legend>执棋顺序</legend>
      <div class="segmented-control">
        <label v-for="item in sideOptions" :key="item.value">
          <input
            type="radio"
            name="traveler-side"
            :value="item.value"
            :checked="travelerSide === item.value"
            :disabled="loading"
            @change="$emit('update:travelerSide', item.value)"
          />
          <span>{{ item.label }}</span>
        </label>
      </div>
    </fieldset>

    <fieldset v-if="showAiLevel" class="settings-field">
      <legend>对手难度</legend>
      <div class="segmented-control difficulty-control">
        <label v-for="item in levelOptions" :key="item.value">
          <input
            type="radio"
            name="ai-level"
            :value="item.value"
            :checked="aiLevel === item.value"
            :disabled="loading"
            @change="$emit('update:aiLevel', item.value)"
          />
          <span>{{ item.label }}</span>
        </label>
      </div>
    </fieldset>

    <fieldset class="settings-field">
      <legend>界面显示</legend>
      <div class="settings-toggle-grid">
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showCellNumbers"
            @change="$emit('update:showCellNumbers', ($event.target as HTMLInputElement).checked)"
          />
          <span>显示格号</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showLegalMoves"
            @change="$emit('update:showLegalMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>显示合法落点</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showWinningMoves"
            @change="$emit('update:showWinningMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>直接胜点</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showThreatMoves"
            @change="$emit('update:showThreatMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>真实威胁</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showRemovalPreview"
            @change="$emit('update:showRemovalPreview', ($event.target as HTMLInputElement).checked)"
          />
          <span>消失预告</span>
        </label>
      </div>
    </fieldset>

    <div class="button-row">
      <button type="button" :disabled="loading" :title="newGameTitle" @click="$emit('newGame')">
        {{ newGameLabel }}
      </button>
      <button type="button" :disabled="loading || !canUndo" :title="undoTitle" @click="$emit('undo')">
        {{ undoLabel }}
      </button>
    </div>
  </section>
</template>
