import { createRouter, createWebHistory } from "vue-router";

import coupleIcon from "../../assets/couple.ico";
import columbinaIcon from "../../assets/columbina.ico";
import sandroneIcon from "../../assets/sandrone.ico";
import LunarOrbitView from "./views/LunarOrbitView.vue";
import MoonHallView from "./views/MoonHallView.vue";
import SilverMoonTeaPartyView from "./views/SilverMoonTeaPartyView.vue";

const routeIcons: Record<string, string> = {
  "moon-hall": coupleIcon,
  "tea-party": columbinaIcon,
  "lunar-orbit": sandroneIcon,
};

function setFavicon(iconUrl: string) {
  let favicon = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
  if (!favicon) {
    favicon = document.createElement("link");
    favicon.rel = "icon";
    document.head.appendChild(favicon);
  }
  favicon.type = "image/x-icon";
  favicon.href = iconUrl;
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "moon-hall",
      component: MoonHallView,
      meta: { title: "月亮棋｜月下对弈" },
    },
    {
      path: "/tea-party",
      name: "tea-party",
      component: SilverMoonTeaPartyView,
      meta: { title: "银月茶会｜月亮棋模拟器" },
    },
    {
      path: "/lunar-orbit",
      name: "lunar-orbit",
      component: LunarOrbitView,
      meta: { title: "月轨推演｜月亮棋模拟器" },
    },
  ],
});

router.afterEach((to) => {
  const iconUrl = routeIcons[String(to.name)];
  if (iconUrl) {
    setFavicon(iconUrl);
  }
  if (to.meta?.title) {
    document.title = to.meta.title as string;
    return;
  }
  document.title = "月亮棋｜月下对弈";
});
