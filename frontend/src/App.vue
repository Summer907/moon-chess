<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterView, useRoute } from "vue-router";

import GameGuideDialog from "./components/GameGuideDialog.vue";

type ThemeMode = "dark" | "light";

const GUIDE_STORAGE_KEY = "moon-chess-guide-seen-v1";
const THEME_STORAGE_KEY = "moon-chess-theme";
const theme = ref<ThemeMode>("dark");
const showGuide = ref(false);
const route = useRoute();

function isThemeMode(value: string | null): value is ThemeMode {
  return value === "dark" || value === "light";
}

function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
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

  if (route.name !== "moon-hall" && window.localStorage.getItem(GUIDE_STORAGE_KEY) !== "true") {
    showGuide.value = true;
  }
});

watch(theme, (value) => {
  syncTheme(value);
});

watch(
  () => route.name,
  (name) => {
    if (name !== "moon-hall" && window.localStorage.getItem(GUIDE_STORAGE_KEY) !== "true") {
      showGuide.value = true;
    }
  },
);
</script>

<template>
  <main class="app-shell" :class="`theme-${theme}`">
    <nav class="app-nav" aria-label="页面导航">
      <div class="app-nav-actions">
        <button type="button" class="nav-icon-button" title="查看规则说明" aria-label="查看规则说明" @click="openGuide">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M5 18.5A2.5 2.5 0 0 1 7.5 16H19" />
            <path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H19v18H7.5A2.5 2.5 0 0 1 5 18.5z" />
            <path d="M8 7h8" />
            <path d="M8 11h6" />
          </svg>
        </button>
        <a
          class="nav-icon-button"
          href="https://github.com/Summer907/moon-chess"
          target="_blank"
          rel="noreferrer"
          title="查看 GitHub 仓库"
          aria-label="查看 GitHub 仓库"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
            <path d="M8 1.5a6.5 6.5 0 0 0-2.06 12.67c.33.06.45-.14.45-.32v-1.2c-1.84.4-2.23-.79-2.23-.79-.3-.76-.73-.96-.73-.96-.6-.41.05-.4.05-.4.66.05 1.01.68 1.01.68.59 1.01 1.54.72 1.92.55.06-.43.23-.72.42-.88-1.47-.17-3.01-.73-3.01-3.25 0-.72.26-1.31.68-1.77-.07-.17-.29-.84.07-1.75 0 0 .55-.18 1.81.68A6.28 6.28 0 0 1 8 4.54c.55 0 1.11.07 1.63.22 1.26-.86 1.81-.68 1.81-.68.36.91.14 1.58.07 1.75.42.46.68 1.05.68 1.77 0 2.53-1.54 3.08-3.01 3.25.24.21.45.62.45 1.25v1.75c0 .18.12.38.46.32A6.5 6.5 0 0 0 8 1.5Z" />
          </svg>
        </a>
        <a
          class="nav-icon-button"
          href="https://space.bilibili.com/11712386"
          target="_blank"
          rel="noreferrer"
          title="访问 Bilibili 主页"
          aria-label="访问 Bilibili 主页"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m8 3.5 2.5 2.5M16 3.5 13.5 6" />
            <rect x="3" y="6" width="18" height="14" rx="4" />
            <path d="M9 11.5v3M15 11.5v3" />
          </svg>
        </a>
        <button
          type="button"
          class="nav-icon-button theme-toggle-button"
          :aria-pressed="theme === 'light'"
          :aria-label="theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'"
          :title="theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'"
          @click="toggleTheme"
        >
          <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.64 5.64l1.42 1.42M16.94 16.94l1.42 1.42M18.36 5.64l-1.42 1.42M7.06 16.94l-1.42 1.42" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5 8.5 8.5 0 1 0 20.5 14.2Z" />
          </svg>
        </button>
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
