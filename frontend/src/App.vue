<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <main class="app-shell">
    <nav class="app-nav" aria-label="页面导航">
      <RouterLink to="/">银月茶会</RouterLink>
      <RouterLink to="/lunar-orbit">月轨推演</RouterLink>
    </nav>

    <RouterView />
  </main>
</template>
