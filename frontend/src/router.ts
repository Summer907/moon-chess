import { createRouter, createWebHistory } from "vue-router";

import coupleIcon from "../../assets/couple.ico";
import columbinaIcon from "../../assets/columbina.ico";
import sandroneIcon from "../../assets/sandrone.ico";
import LunarOrbitView from "./views/LunarOrbitView.vue";
import MoonHallView from "./views/MoonHallView.vue";
import SilverMoonTeaPartyView from "./views/SilverMoonTeaPartyView.vue";
import { syncDocumentTitle } from "./i18n/locale";

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
      meta: { titleKey: "meta.moonHall" },
    },
    {
      path: "/tea-party",
      name: "tea-party",
      component: SilverMoonTeaPartyView,
      meta: { titleKey: "meta.teaParty" },
    },
    {
      path: "/lunar-orbit",
      name: "lunar-orbit",
      component: LunarOrbitView,
      meta: { titleKey: "meta.lunarOrbit" },
    },
  ],
});

router.afterEach((to) => {
  const iconUrl = routeIcons[String(to.name)];
  if (iconUrl) {
    setFavicon(iconUrl);
  }
  syncDocumentTitle(to);
});
