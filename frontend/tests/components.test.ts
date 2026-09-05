import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import GameCell from "../src/components/GameCell.vue";
import GameStatusCard from "../src/components/game/GameStatusCard.vue";
import { zhCN } from "../src/i18n/locales/zh-CN";
import { enUS } from "../src/i18n/locales/en-US";
import { createPlayerDisplay } from "../src/utils/playerDisplay";
import type { GameState } from "../src/types/game";

const i18n = () => createI18n({ legacy: false, locale: "zh-CN", messages: { "zh-CN": zhCN, "en-US": enUS } });

describe("accessible game facts", () => {
  it("announces analysis markers and does not allow disabled moves", async () => {
    const wrapper = mount(GameCell, {
      global: { plugins: [i18n()] },
      props: { position: 3, piece: null, showNumber: true, isPendingRemoval: false,
        isWinning: false, isLegal: true, showLegalHighlight: true, isCurrentWinningMove: true,
        isOpponentRealThreat: true, isLastMove: true, disabled: true },
    });
    expect(wrapper.attributes("aria-label")).toContain("胜点");
    expect(wrapper.attributes("aria-label")).toContain("威胁");
    expect(wrapper.attributes("aria-label")).toContain("上一手");
    await wrapper.trigger("click");
    expect(wrapper.emitted("place")).toBeUndefined();
    wrapper.unmount();
  });
  it("renders a supplied AI status and localizes a draw", async () => {
    const plugin = i18n();
    const state = {
      game_id: "test", revision: 0, current_player: "X", move_number: 0,
      status: "playing", pending_removal: null, upcoming_removal: null, legal_moves: [1], winning_line: null,
    } as GameState;
    const wrapper = mount(GameStatusCard, {
      global: { plugins: [plugin] },
      props: { state, displayMap: createPlayerDisplay("first", key => plugin.global.t(key)),
        showRemovalPreview: true, aiThinking: true, thinkingText: "哥伦比娅思考中…" },
    });
    expect(wrapper.text()).toContain("哥伦比娅思考中…");
    await wrapper.setProps({ state: { ...state, status: "draw", move_number: 14 } });
    expect(wrapper.text()).toContain("平局");
    plugin.global.locale.value = "en-US";
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain("Draw");
    wrapper.unmount();
  });
});
