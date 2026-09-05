import { computed, onBeforeUnmount, ref } from "vue";
import { ApiError, getGame } from "../api/client";
import type { GameState } from "../types/game";

export function useGameSession() {
  const gameState = ref<GameState | null>(null);
  const phase = ref<"loading" | "ready" | "thinking" | "submitting" | "syncing" | "failed">("loading");
  const failure = ref<unknown>(null);
  const needsSync = ref(false);
  const retryAfter = ref(0);
  let generation = 0;
  let controller: AbortController | undefined;
  let disposed = false;
  const ticker = setInterval(() => { retryAfter.value = Math.max(0, retryAfter.value - 1); }, 1000);
  const loading = computed(() => ["loading", "submitting", "syncing"].includes(phase.value));
  const blocked = computed(() => loading.value || needsSync.value || retryAfter.value > 0);

  function setFailure(error: unknown) {
    failure.value = error;
    retryAfter.value = error instanceof ApiError ? error.retryAfter : 0;
    if (error instanceof ApiError && error.code === "game_not_found") {
      gameState.value = null;
      needsSync.value = false;
    }
    phase.value = "failed";
  }

  async function run(action: (signal: AbortSignal) => Promise<GameState>, create = false) {
    if (disposed || loading.value && controller || retryAfter.value > 0) return null;
    const token = ++generation;
    controller?.abort();
    controller = new AbortController();
    const signal = controller.signal;
    phase.value = create ? "loading" : "submitting";
    failure.value = null;
    if (create) { gameState.value = null; needsSync.value = false; }
    try {
      const state = await action(signal);
      if (token !== generation || disposed) return null;
      gameState.value = state;
      needsSync.value = false;
      phase.value = "ready";
      return state;
    } catch (error) {
      if (token !== generation || disposed) return null;
      setFailure(error);
      if (!create && gameState.value && (!(error instanceof ApiError) || error.status >= 500 || error.code === "state_conflict")) {
        needsSync.value = true;
        phase.value = "syncing";
        try {
          const state = await getGame(gameState.value.game_id, signal);
          if (token !== generation || disposed) return null;
          gameState.value = state;
          needsSync.value = false;
          phase.value = "failed";
        } catch (syncError) {
          if (token === generation && !disposed) setFailure(syncError);
        }
      }
      return null;
    } finally {
      if (token === generation) controller = undefined;
    }
  }

  async function synchronize() {
    if (!gameState.value) return null;
    const id = gameState.value.game_id;
    return run(signal => getGame(id, signal));
  }

  onBeforeUnmount(() => {
    disposed = true;
    generation++;
    controller?.abort();
    clearInterval(ticker);
  });
  return { gameState, phase, failure, needsSync, retryAfter, loading, blocked, run, synchronize };
}
