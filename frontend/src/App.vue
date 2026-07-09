<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, RouterView } from "vue-router";

import GameGuideDialog from "./components/GameGuideDialog.vue";

type ThemeMode = "dark" | "light";

const GUIDE_STORAGE_KEY = "moon-chess-guide-seen-v1";
const THEME_STORAGE_KEY = "moon-chess-theme";
const theme = ref<ThemeMode>("dark");
const showGuide = ref(false);

function isThemeMode(value: string | null): value is ThemeMode {
  return value === "dark" || value === "light";
}

function setTheme(value: ThemeMode) {
  theme.value = value;
}

function openGuide() {
  showGuide.value = true;
}

function closeGuide() {
  showGuide.value = false;
  window.localStorage.setItem(GUIDE_STORAGE_KEY, "true");
}

function syncTheme(value: ThemeMode) {
  document.documentElement.dataset.theme = value;
  document.documentElement.style.colorScheme = value;
  window.localStorage.setItem(THEME_STORAGE_KEY, value);
}

onMounted(() => {
  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (isThemeMode(savedTheme)) {
    theme.value = savedTheme;
  }
  syncTheme(theme.value);

  if (window.localStorage.getItem(GUIDE_STORAGE_KEY) !== "true") {
    showGuide.value = true;
  }
});

watch(theme, (value) => {
  syncTheme(value);
});
</script>

<template>
  <main class="app-shell" :class="`theme-${theme}`">
    <nav class="app-nav" aria-label="页面导航">
      <div class="app-nav-links">
        <RouterLink to="/">银月茶会</RouterLink>
        <RouterLink to="/lunar-orbit">月轨推演</RouterLink>
      </div>
      <div class="app-nav-actions">
        <button type="button" class="nav-icon-button" title="查看规则说明" aria-label="查看规则说明" @click="openGuide">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z" />
            <path d="M8 7h8" />
            <path d="M8 11h6" />
          </svg>
        </button>
        <a
          class="nav-icon-button nav-icon-button--github"
          href="https://github.com/Summer907/moon-chess"
          target="_blank"
          rel="noreferrer"
          title="查看 GitHub 仓库"
          aria-label="查看 GitHub 仓库"
        >
          <svg viewBox="1.5 1.5 13 13" fill="currentColor" aria-hidden="true">
            <path d="M8 1.5a6.5 6.5 0 0 0-2.06 12.67c.33.06.45-.14.45-.32v-1.2c-1.84.4-2.23-.79-2.23-.79-.3-.76-.73-.96-.73-.96-.6-.41.05-.4.05-.4.66.05 1.01.68 1.01.68.59 1.01 1.54.72 1.92.55.06-.43.23-.72.42-.88-1.47-.17-3.01-.73-3.01-3.25 0-.72.26-1.31.68-1.77-.07-.17-.29-.84.07-1.75 0 0 .55-.18 1.81.68A6.28 6.28 0 0 1 8 4.54c.55 0 1.11.07 1.63.22 1.26-.86 1.81-.68 1.81-.68.36.91.14 1.58.07 1.75.42.46.68 1.05.68 1.77 0 2.53-1.54 3.08-3.01 3.25.24.21.45.62.45 1.25v1.75c0 .18.12.38.46.32A6.5 6.5 0 0 0 8 1.5Z" />
          </svg>
        </a>
        <div class="theme-switcher" aria-label="主题切换">
          <button
            type="button"
            class="nav-icon-button theme-toggle-button"
            :class="{ active: theme === 'dark' }"
            :aria-pressed="theme === 'dark'"
            @click="setTheme('dark')"
            aria-label="深色模式"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
              <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
          </button>
          <button
            type="button"
            class="nav-icon-button theme-toggle-button"
            :class="{ active: theme === 'light' }"
            :aria-pressed="theme === 'light'"
            @click="setTheme('light')"
            aria-label="浅色模式"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
              <path d="M12 7a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0-5a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0V3a1 1 0 0 0-1-1zm0 16a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-1-1zm9-8h-2a1 1 0 0 0 0 2h2a1 1 0 0 0 0-2zM5 12a1 1 0 0 0-1-1H2a1 1 0 0 0 0 2h2a1 1 0 0 0 1-1zm.636-5.364a1 1 0 0 0 1.414 0 .999.999 0 0 0 0-1.414l-1.414-1.414a1 1 0 0 0-1.414 1.414zm14.142 0-1.414-1.414a1 1 0 0 0-1.414 1.414 1 1 0 0 0 1.414 0zM6.05 17.364a1 1 0 0 0-1.414 0l-1.414 1.414a1 1 0 1 0 1.414 1.414l1.414-1.414a1 1 0 0 0 0-1.414zm12.9 0a1 1 0 0 0 0 1.414l1.414 1.414a1 1 0 0 0 1.414-1.414l-1.414-1.414a1 1 0 0 0-1.414 0z"/>
            </svg>
          </button>
        </div>
      </div>
    </nav>

    <RouterView />
    <footer class="app-footer">
      <p>© 2026 Summer907 · MIT License</p>
      <p>玩家自制规则演示工具，与游戏官方无关联。</p>
    </footer>
    <GameGuideDialog v-if="showGuide" @close="closeGuide" />
  </main>
</template>
