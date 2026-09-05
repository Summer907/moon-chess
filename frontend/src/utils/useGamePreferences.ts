import type { AiLevel } from "../types/game";
import type { TravelerSide } from "../types/display";

const STORAGE_KEY = "moon-chess-preferences-v1";

export interface DisplayPreferences { numbers: boolean; legal: boolean; wins: boolean; threats: boolean; removal: boolean; }
export const defaultDisplay: DisplayPreferences = { numbers: true, legal: true, wins: true, threats: true, removal: true };

function displayPreferences(value?: Partial<DisplayPreferences>): DisplayPreferences {
  return Object.fromEntries(Object.entries(defaultDisplay).map(([key, fallback]) => [key, typeof value?.[key as keyof DisplayPreferences] === "boolean" ? value[key as keyof DisplayPreferences] : fallback])) as unknown as DisplayPreferences;
}

export interface MoonChessPreferences {
  teaParty: {
    display: DisplayPreferences;
    travelerSide: TravelerSide;
    aiLevel: AiLevel;
  };
  lunarOrbit: {
    display: DisplayPreferences;
    travelerSide: TravelerSide;
  };
}

const defaults: MoonChessPreferences = {
  teaParty: { display: { ...defaultDisplay }, travelerSide: "first", aiLevel: "medium" },
  lunarOrbit: { display: { ...defaultDisplay }, travelerSide: "first" },
};

function isTravelerSide(value: unknown): value is TravelerSide {
  return value === "first" || value === "second";
}

function isAiLevel(value: unknown): value is AiLevel {
  return value === "easy" || value === "medium" || value === "hard";
}

export function loadGamePreferences(): MoonChessPreferences {
  try {
    const saved = window.sessionStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return structuredClone(defaults);
    }
    const parsed = JSON.parse(saved) as Partial<MoonChessPreferences>;
    return {
      teaParty: {
        display: displayPreferences(parsed.teaParty?.display),
        travelerSide: isTravelerSide(parsed.teaParty?.travelerSide) ? parsed.teaParty.travelerSide : defaults.teaParty.travelerSide,
        aiLevel: isAiLevel(parsed.teaParty?.aiLevel) ? parsed.teaParty.aiLevel : defaults.teaParty.aiLevel,
      },
      lunarOrbit: {
        display: displayPreferences(parsed.lunarOrbit?.display),
        travelerSide: isTravelerSide(parsed.lunarOrbit?.travelerSide) ? parsed.lunarOrbit.travelerSide : defaults.lunarOrbit.travelerSide,
      },
    };
  } catch {
    return structuredClone(defaults);
  }
}

export function saveGamePreferences(preferences: MoonChessPreferences) {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  } catch {
    // Starting a game must not depend on session storage availability.
  }
}
