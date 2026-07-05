from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .game import GameError, GameStore
from .models import CreateGameRequest, GameState, MoveRequest


app = FastAPI(title="Moon Chess API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = GameStore()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/games", response_model=GameState)
def create_game(request: CreateGameRequest | None = None) -> GameState:
    payload = request or CreateGameRequest()
    return store.create(
        first_player=payload.first_player,
        draw_mode=payload.draw_mode,
        max_moves=payload.max_moves,
    )


@app.get("/api/games/{game_id}", response_model=GameState)
def get_game(game_id: str) -> GameState:
    try:
        return store.get(game_id).state()
    except GameError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/games/{game_id}/moves", response_model=GameState)
def make_move(game_id: str, request: MoveRequest) -> GameState:
    try:
        return store.get(game_id).move(request.position)
    except GameError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/games/{game_id}/undo", response_model=GameState)
def undo(game_id: str) -> GameState:
    try:
        return store.get(game_id).undo()
    except GameError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/games/{game_id}/reset", response_model=GameState)
def reset(game_id: str) -> GameState:
    try:
        return store.get(game_id).reset()
    except GameError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
