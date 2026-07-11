import type { AiLevel } from "../types/game";
import type { TravelerSide } from "../types/display";

const STORAGE_KEY = "moon-chess-preferences-v1";

export interface MoonChessPreferences {
  teaParty: {
    travelerSide: TravelerSide;
    aiLevel: AiLevel;
  };
  lunarOrbit: {
    travelerSide: TravelerSide;
  };
}

const defaults: MoonChessPreferences = {
  teaParty: { travelerSide: "first", aiLevel: "medium" },
  lunarOrbit: { travelerSide: "first" },
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
        travelerSide: isTravelerSide(parsed.teaParty?.travelerSide) ? parsed.teaParty.travelerSide : defaults.teaParty.travelerSide,
        aiLevel: isAiLevel(parsed.teaParty?.aiLevel) ? parsed.teaParty.aiLevel : defaults.teaParty.aiLevel,
      },
      lunarOrbit: {
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
