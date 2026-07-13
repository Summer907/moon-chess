import type { RouteLocationNormalizedLoaded } from "vue-router";
import { i18n } from "./index";

export type SupportedLocale = "zh-CN" | "en-US";
const KEY = "moon-chess-locale-v1";
export const isSupportedLocale = (value: unknown): value is SupportedLocale => value === "zh-CN" || value === "en-US";
export function detectLocale(): SupportedLocale { try { const saved = localStorage.getItem(KEY); if (isSupportedLocale(saved)) return saved; } catch {} const language = navigator.languages?.[0] ?? navigator.language; return language ? (language.toLowerCase().startsWith("zh") ? "zh-CN" : "en-US") : "zh-CN"; }
export function setLocale(locale: SupportedLocale, persist = true) { i18n.global.locale.value = locale; document.documentElement.lang = locale; if (persist) try { localStorage.setItem(KEY, locale); } catch {} }
export function initializeLocale() { setLocale(detectLocale(), false); }
export function toggleLocale() { setLocale(i18n.global.locale.value === "zh-CN" ? "en-US" : "zh-CN"); }
export function syncDocumentTitle(route: RouteLocationNormalizedLoaded) { const key = route.meta.titleKey; document.title = typeof key === "string" ? i18n.global.t(key) : i18n.global.t("meta.moonHall"); }
