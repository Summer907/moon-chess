<script setup lang="ts">
import type { PlayerDisplayMap } from "../../types/display";
import type { MoveEvent } from "../../types/game";
import { useI18n } from "vue-i18n";
import { formatPieceFull, formatPlayer } from "../../utils/playerDisplay";

defineProps<{
  history: MoveEvent[];
  displayMap: PlayerDisplayMap;
}>();
const { t } = useI18n();
function formatMoveEvent(event: MoveEvent, displayMap: PlayerDisplayMap): string {
  const piece = formatPieceFull(event.placed_piece, displayMap, t("common.none"));
  const removed = event.removed_piece ? formatPieceFull(event.removed_piece, displayMap, t("common.none")) : "";
  const key = event.removal_phase === "before_move" ? "game.moveEventBefore" : event.removal_phase === "after_move" ? "game.moveEventAfter" : "game.moveEvent";
  const base = t(key, { count: event.move_number, piece, removed, position: event.position });
  return event.winner ? t("game.moveEventWinner", { event: base, player: formatPlayer(event.winner, displayMap, t("common.none")) }) : base;
}
</script>

<template>
  <section class="history-panel game-history-panel" :aria-label="t('history.title')">
    <div class="section-title">
      <span>{{ t('history.title') }}</span>
      <strong>{{ t('history.count', { count: history.length }) }}</strong>
    </div>

    <div class="history-scroll">
      <ul v-if="history.length > 0" class="history-list">
        <li v-for="event in history" :key="event.move_number">
          {{ formatMoveEvent(event, displayMap) }}
        </li>
      </ul>
      <p v-else class="empty-text">{{ t('history.empty') }}</p>
    </div>
  </section>
</template>
