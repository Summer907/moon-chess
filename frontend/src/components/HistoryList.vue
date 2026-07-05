<script setup lang="ts">
import type { MoveEvent } from "../types/game";

defineProps<{
  history: MoveEvent[];
}>();
</script>

<template>
  <section class="history-panel" aria-label="棋谱历史">
    <div class="section-title">
      <span>棋谱历史</span>
      <strong>{{ history.length }} 手</strong>
    </div>

    <div class="history-scroll">
      <ul v-if="history.length > 0" class="history-list">
        <li v-for="event in history" :key="event.move_number">
          {{ event.note }}
        </li>
      </ul>
      <p v-else class="empty-text">尚未落子。</p>
    </div>
  </section>
</template>
