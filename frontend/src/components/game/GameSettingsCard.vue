<script setup lang="ts">
import type { TravelerSide } from "../../types/display";
import type { AiLevel } from "../../types/game";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = withDefaults(
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
    title: "", newGameLabel: "", newGameTitle: "", undoLabel: "", undoTitle: "",
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

const { t } = useI18n();
const sideOptions = computed(() => [{ value: "first" as const, label: t("settings.first") }, { value: "second" as const, label: t("settings.second") }]);
const levelOptions = computed(() => [{ value: "easy" as const, label: t("difficulty.easy") }, { value: "medium" as const, label: t("difficulty.medium") }, { value: "hard" as const, label: t("difficulty.hard") }]);
const cardTitle = computed(() => props.title || t("settings.configuration"));
const newLabel = computed(() => props.newGameLabel || t("teaParty.restart"));
const newTitle = computed(() => props.newGameTitle || t("teaParty.restartTitle"));
const undoLabelText = computed(() => props.undoLabel || t("teaParty.undo"));
const undoTitleText = computed(() => props.undoTitle || t("teaParty.undoTitle"));
</script>

<template>
  <section class="game-settings-card" :aria-label="t('settings.configuration')">
    <div class="section-title">
      <span>{{ cardTitle }}</span>
    </div>

    <fieldset class="settings-field">
      <legend>{{ t('settings.side') }}</legend>
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
      <legend>{{ t('settings.opponentDifficulty') }}</legend>
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
      <legend>{{ t('settings.display') }}</legend>
      <div class="settings-toggle-grid">
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showCellNumbers"
            @change="$emit('update:showCellNumbers', ($event.target as HTMLInputElement).checked)"
          />
          <span>{{ t('settings.numbers') }}</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showLegalMoves"
            @change="$emit('update:showLegalMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>{{ t('settings.legal') }}</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showWinningMoves"
            @change="$emit('update:showWinningMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>{{ t('settings.wins') }}</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showThreatMoves"
            @change="$emit('update:showThreatMoves', ($event.target as HTMLInputElement).checked)"
          />
          <span>{{ t('settings.threats') }}</span>
        </label>
        <label class="toggle-row">
          <input
            type="checkbox"
            :checked="showRemovalPreview"
            @change="$emit('update:showRemovalPreview', ($event.target as HTMLInputElement).checked)"
          />
          <span>{{ t('settings.preview') }}</span>
        </label>
      </div>
    </fieldset>

    <div class="button-row">
      <button type="button" :disabled="loading" :title="newTitle" @click="$emit('newGame')">
        {{ newLabel }}
      </button>
      <button type="button" :disabled="loading || !canUndo" :title="undoTitleText" @click="$emit('undo')">
        {{ undoLabelText }}
      </button>
    </div>
  </section>
</template>
