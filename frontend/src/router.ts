import { createRouter, createWebHistory } from "vue-router";

import AiBattleView from "./views/AiBattleView.vue";
import ClassicGameView from "./views/ClassicGameView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "classic",
      component: ClassicGameView,
    },
    {
      path: "/ai",
      name: "ai",
      component: AiBattleView,
    },
  ],
});
