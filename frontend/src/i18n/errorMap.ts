import type { Composer } from "vue-i18n";
import { ApiError } from "../api/client";

const keys: Record<string, string> = { owner_capacity_reached: "recovery.ownerCapacity", state_conflict: "recovery.conflict", game_not_found: "errors.gameNotFound", game_finished: "errors.gameFinished", invalid_move: "errors.invalidMove", no_legal_moves: "errors.noLegalMoves", game_capacity_reached: "errors.gameCapacity", rate_limited: "errors.rateLimited", ai_busy: "errors.aiBusy", validation_error: "errors.validation" };
export function errorText(error: unknown, t: Composer["t"]): string {
  if (error instanceof ApiError) return t(keys[error.code] ?? "errors.generic", { status: error.status, ...error.params });
  return t("errors.network");
}
