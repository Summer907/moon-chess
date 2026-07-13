<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

const emit = defineEmits<{
  close: [];
}>();

type GuideTab = "quick" | "rules" | "modes" | "markers";

const activeTab = ref<GuideTab>("quick");
const dialogRef = ref<HTMLElement | null>(null);

const { t } = useI18n();
const tabs: Array<{ id: GuideTab; key: string }> = [
  { id: "quick", key: "guide.quick" }, { id: "rules", key: "guide.rules" }, { id: "modes", key: "guide.modes" }, { id: "markers", key: "guide.markers" },
];

function closeDialog() {
  emit("close");
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape") {
    closeDialog();
  }
}

onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
  void nextTick(() => {
    dialogRef.value?.focus();
  });
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <Teleport to="body">
    <div class="guide-backdrop" role="presentation" @click.self="closeDialog">
      <section
        ref="dialogRef"
        class="guide-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guide-title"
        tabindex="-1"
      >
        <header class="guide-header">
          <div>
            <p class="guide-kicker">{{ t('guide.kicker') }}</p><h2 id="guide-title">{{ t('guide.title') }}</h2>
          </div>
          <button type="button" class="guide-icon-button" :title="t('guide.close')" :aria-label="t('guide.closeAria')" @click="closeDialog">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </svg>
          </button>
        </header>

        <div class="guide-tabs" role="tablist" :aria-label="t('guide.content')">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            class="guide-tab"
            :class="{ active: activeTab === tab.id }"
            role="tab"
            :aria-selected="activeTab === tab.id"
            @click="activeTab = tab.id"
          >
            {{ t(tab.key) }}
          </button>
        </div>

        <div class="guide-content">
          <section v-if="activeTab === 'quick'" class="guide-panel" role="tabpanel">
            <div class="guide-callout">
              <strong>{{ t('guide.oneLine') }}</strong><p>{{ t('guide.oneLineText') }}</p>
            </div>
            <ol class="guide-steps">
              <li>{{ t('guide.step1') }}</li><li>{{ t('guide.step2') }}</li><li>{{ t('guide.step3') }}</li><li>{{ t('guide.step4') }}</li>
            </ol>
          </section>

          <section v-else-if="activeTab === 'rules'" class="guide-panel" role="tabpanel">
            <dl class="guide-rule-list">
              <div>
                <dt>{{ t('guide.board') }}</dt>
                <dd>{{ t('guide.boardText') }}</dd>
              </div>
              <div>
                <dt>{{ t('guide.move') }}</dt>
                <dd>{{ t('guide.moveText') }}</dd>
              </div>
              <div>
                <dt>{{ t('guide.removal') }}</dt>
                <dd>{{ t('guide.removalText') }}</dd>
              </div>
              <div>
                <dt>{{ t('guide.result') }}</dt>
                <dd>{{ t('guide.resultText') }}</dd>
              </div>
            </dl>
          </section>

          <section v-else-if="activeTab === 'modes'" class="guide-panel" role="tabpanel">
            <div class="guide-mode-grid">
              <article>
                <h3>{{ t('home.teaTitle') }}</h3>
                <p>{{ t('guide.teaText') }}</p>
              </article>
              <article>
                <h3>{{ t('home.orbitTitle') }}</h3>
                <p>{{ t('guide.orbitText') }}</p>
              </article>
            </div>
          </section>

          <section v-else class="guide-panel" role="tabpanel">
            <ul class="guide-marker-list">
              <li><strong>{{ t('guide.number') }}</strong><span>{{ t('guide.numberText') }}</span></li>
              <li><strong>{{ t('guide.legal') }}</strong><span>{{ t('guide.legalText') }}</span></li>
              <li><strong>{{ t('guide.win') }}</strong><span>{{ t('guide.winText') }}</span></li>
              <li><strong>{{ t('guide.threat') }}</strong><span>{{ t('guide.threatText') }}</span></li>
              <li><strong>{{ t('guide.preview') }}</strong><span>{{ t('guide.previewText') }}</span></li>
            </ul>
          </section>
        </div>
      </section>
    </div>
  </Teleport>
</template>
