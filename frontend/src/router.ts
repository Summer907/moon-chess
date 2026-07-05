import { createRouter, createWebHistory } from "vue-router";

import LunarOrbitView from "./views/LunarOrbitView.vue";
import SilverMoonTeaPartyView from "./views/SilverMoonTeaPartyView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "tea-party",
      component: SilverMoonTeaPartyView,
    },
    {
      path: "/lunar-orbit",
      name: "lunar-orbit",
      component: LunarOrbitView,
      meta: { title: "月轨推演｜月亮棋模拟器" },
    },
  ],
});

router.afterEach((to, from) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string;
    return;
  }
  if (to.name === "tea-party" && from.name === "lunar-orbit") {
    document.title = "银月茶会｜月亮棋模拟器";
    return;
  }
  document.title = "月亮棋模拟器｜银月茶会与月轨推演";
});
