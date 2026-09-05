import { describe, it, expect, vi, afterEach } from "vitest";
import { defineComponent } from "vue";
import { mount } from "@vue/test-utils";
import { useGameSession } from "../src/utils/useGameSession";
import { loadGamePreferences, saveGamePreferences } from "../src/utils/useGamePreferences";
import { createGame, makeMove } from "../src/api/client";
import type { GameState } from "../src/types/game";

const state = (revision = 0) => ({ game_id: "test", revision, move_number: revision } as GameState);
function harness() {
  let session!: ReturnType<typeof useGameSession>;
  const wrapper = mount(defineComponent({ setup() { session = useGameSession(); return () => null; } }));
  return { session, wrapper };
}
afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); sessionStorage.clear(); });

describe("request recovery", () => {
  it("synchronizes a lost mutation response without replaying it", async () => {
    const { session, wrapper } = harness();
    await session.run(async () => state(), true);
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(state(1))));
    vi.stubGlobal("fetch", fetch);
    const mutation = vi.fn().mockRejectedValue(new TypeError("network"));
    await session.run(mutation);
    expect(mutation).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(session.gameState.value?.revision).toBe(1);
    expect(session.needsSync.value).toBe(false);
    wrapper.unmount();
  });
  it("blocks moves if reconciliation also fails", async () => {
    const { session, wrapper } = harness();
    await session.run(async () => state(), true);
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    await session.run(async () => { throw new TypeError("offline"); });
    expect(session.needsSync.value).toBe(true);
    expect(session.blocked.value).toBe(true);
    wrapper.unmount();
  });
  it("ignores a response after unmount", async () => {
    const { session, wrapper } = harness();
    let resolve!: (value: GameState) => void;
    const pending = session.run(() => new Promise<GameState>(done => { resolve = done; }), true);
    wrapper.unmount();
    resolve(state(2));
    await pending;
    expect(session.gameState.value).toBeNull();
  });
  it("times out ordinary requests and sends the revision", async () => {
    vi.useFakeTimers();
    const fetch = vi.fn((_url, init) => new Promise((_resolve, reject) => {
      init.signal.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
    }));
    vi.stubGlobal("fetch", fetch);
    const pending = makeMove("test", 5, 7);
    const assertion = expect(pending).rejects.toThrow("Aborted");
    await vi.advanceTimersByTimeAsync(15000);
    await assertion;
    expect(JSON.parse(fetch.mock.calls[0]![1].body).expected_revision).toBe(7);
  });
  it("keeps Retry-After and exposes a creation failure", async () => {
    const { session, wrapper } = harness();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      detail: { code: "rate_limited", params: { retry_after: 3 } },
    }), { status: 429, headers: { "Retry-After": "3" } })));
    await session.run(signal => createGame({}, signal), true);
    expect(session.retryAfter.value).toBe(3);
    expect(session.phase.value).toBe("failed");
    wrapper.unmount();
  });
});

it("preserves independent display preferences and accepts old saved preferences", () => {
  sessionStorage.setItem("moon-chess-preferences-v1", JSON.stringify({ teaParty: { travelerSide: "second" } }));
  const prefs = loadGamePreferences();
  expect(prefs.teaParty.travelerSide).toBe("second");
  expect(prefs.teaParty.display.wins).toBe(true);
  prefs.teaParty.display.wins = false;
  saveGamePreferences(prefs);
  expect(loadGamePreferences().teaParty.display.wins).toBe(false);
  expect(loadGamePreferences().lunarOrbit.display.wins).toBe(true);
});
