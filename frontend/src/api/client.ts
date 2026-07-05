import type { CreateGameRequest, GameState } from "../types/game";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    let message = `请求失败：${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the generic message when the server does not return JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function createGame(payload: CreateGameRequest = {}): Promise<GameState> {
  return request<GameState>("/api/games", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getGame(gameId: string): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}`);
}

export function makeMove(gameId: string, position: number): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}/moves`, {
    method: "POST",
    body: JSON.stringify({ position }),
  });
}

export function undo(gameId: string): Promise<GameState> {
  return request<GameState>(`/api/games/${gameId}/undo`, {
    method: "POST",
  });
}
