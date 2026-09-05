import type { AiLevel, AiMoveRequest, AiMoveResponse, CreateGameRequest, GameState } from "../types/game";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error { constructor(public status: number, public code: string, public params: Record<string, unknown>, public retryAfter = 0) { super(code); } }
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  init?.signal?.addEventListener("abort", abort, { once: true });
  if (init?.signal?.aborted) controller.abort();
  const timer = setTimeout(abort, path.includes("ai-move") || path.includes("hint") ? 30000 : 15000);
  try {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    signal: controller.signal,
  });

  if (!response.ok) {
    let code = "unknown";
    let params: Record<string, unknown> = {};
    try {
      const body = (await response.json()) as { detail?: { code?: string; params?: Record<string, unknown> } };
      if (body.detail?.code) { code = body.detail.code; params = body.detail.params ?? {}; }
    } catch {
      // Keep the generic message when the server does not return JSON.
    }
    throw new ApiError(response.status, code, params, Math.max(0, Number(response.headers.get("Retry-After")) || 0));
  }

  return await response.json() as T;
  } finally { clearTimeout(timer); init?.signal?.removeEventListener("abort", abort); }
}

export function createGame(payload: CreateGameRequest = {}, signal?: AbortSignal): Promise<GameState> {
  return request<GameState>("/api/games", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function getGame(gameId: string, signal?: AbortSignal): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}`, { signal });
}

export function makeMove(gameId: string, position: number, expected_revision?: number, signal?: AbortSignal): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}/moves`, {
    method: "POST",
    body: JSON.stringify({ position, expected_revision }),
    signal,
  });
}

export function getHint(gameId: string, level: AiLevel = "medium", seed?: number | null): Promise<AiMoveResponse> {
  const params = new URLSearchParams({ level });
  if (seed !== undefined && seed !== null) {
    params.set("seed", String(seed));
  }
  return request<AiMoveResponse>(`/api/games/${gameId}/hint?${params.toString()}`);
}

export function makeAiMove(gameId: string, payload: AiMoveRequest = {}, signal?: AbortSignal): Promise<AiMoveResponse> {
  return request<AiMoveResponse>(`/api/games/${gameId}/ai-move`, {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function undo(gameId: string, expected_revision?: number, steps = 1, signal?: AbortSignal): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}/undo`, {
    method: "POST",
    body: JSON.stringify({ expected_revision, steps }),
    signal,
  });
}

export function resetGame(gameId: string, expected_revision: number, signal?: AbortSignal): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}/reset`, {
    method: "POST",
    body: JSON.stringify({ expected_revision }),
    signal,
  });
}
