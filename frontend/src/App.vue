<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, RouterView } from "vue-router";

type ThemeMode = "dark" | "light";

const THEME_STORAGE_KEY = "moon-chess-theme";
const theme = ref<ThemeMode>("dark");

function isThemeMode(value: string | null): value is ThemeMode {
  return value === "dark" || value === "light";
}

function setTheme(value: ThemeMode) {
  theme.value = value;
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
      <div class="theme-switcher" aria-label="主题切换">
        <button
          type="button"
          class="theme-toggle-button"
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
          class="theme-toggle-button"
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
    </nav>

    <RouterView />
  </main>
</template>
