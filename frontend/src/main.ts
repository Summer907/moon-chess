import { createApp } from "vue";

import App from "./App.vue";
import { router } from "./router";
import { i18n } from "./i18n";
import { initializeLocale } from "./i18n/locale";
import "./styles/global.css";

initializeLocale();
createApp(App).use(i18n).use(router).mount("#app");
