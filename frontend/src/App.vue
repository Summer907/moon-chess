<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <main class="app-shell">
    <nav class="app-nav" aria-label="页面导航">
      <RouterLink to="/">普通对局</RouterLink>
      <RouterLink to="/ai">AI 对战</RouterLink>
    </nav>

    <RouterView />
  </main>
</template>
