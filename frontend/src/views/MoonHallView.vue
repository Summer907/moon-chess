<script setup lang="ts">
import { useI18n } from "vue-i18n";
const { t } = useI18n();
</script>

<template>
  <section class="moon-hall" aria-labelledby="moon-hall-title">
    <div class="moon-hall__aura" aria-hidden="true"></div>
    <header class="moon-hall__hero">
      <p class="moon-hall__eyebrow">Moon Chess</p>
      <h1 id="moon-hall-title">{{ t('home.title') }}</h1>
      <p>{{ t('home.subtitle') }}</p>
    </header>

    <div class="mode-card-grid" :aria-label="t('home.modes')">
      <RouterLink class="mode-card mode-card--tea" to="/tea-party" :aria-label="t('home.teaAria')">
        <div class="mode-card__illustration mode-card__illustration--tea" aria-hidden="true">
          <div class="piece-columbina"><span class="piece-label"></span></div>
          <div class="piece-traveler"><span class="piece-label"></span></div>
        </div>
        <p class="mode-card__kicker">{{ t('home.ai') }}</p><h2>{{ t('home.teaTitle') }}</h2><p>{{ t('home.teaText') }}</p>
        <ul :aria-label="t('home.teaFeatures')">
          <li>{{ t('home.levels') }}</li><li>{{ t('home.autoReply') }}</li><li>{{ t('home.history') }}</li>
        </ul>
        <span class="mode-card__enter">{{ t('home.enterTea') }} <span aria-hidden="true">→</span></span>
      </RouterLink>

      <RouterLink class="mode-card mode-card--orbit" to="/lunar-orbit" :aria-label="t('home.orbitAria')">
        <div class="mode-card__illustration mode-card__illustration--orbit" aria-hidden="true">
          <span></span><span></span><span></span>
        </div>
        <p class="mode-card__kicker">{{ t('home.free') }}</p><h2>{{ t('home.orbitTitle') }}</h2><p>{{ t('home.orbitText') }}</p>
        <ul :aria-label="t('home.orbitFeatures')">
          <li>{{ t('home.backend') }}</li><li>{{ t('home.threats') }}</li><li>{{ t('home.undo') }}</li>
        </ul>
        <span class="mode-card__enter">{{ t('home.enterOrbit') }} <span aria-hidden="true">→</span></span>
      </RouterLink>
    </div>
    <!-- <p class="moon-hall__note">选择模式后即可开始；开局设置会在对应页面保留。</p> -->
  </section>
</template>
