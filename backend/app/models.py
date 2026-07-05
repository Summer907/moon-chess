from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Player = Literal["X", "O"]
GameStatus = Literal["playing", "won", "draw"]
DrawMode = Literal["repetition"]


class Piece(BaseModel):
    id: str
    player: Player
    position: int = Field(ge=1, le=9)
    order: int = Field(ge=1)


class MoveEvent(BaseModel):
    move_number: int = Field(ge=1)
    player: Player
    removed_piece: Piece | None
    placed_piece: Piece
    position: int = Field(ge=1, le=9)
    winner: Player | None
    line: list[int] | None
    note: str


class Analysis(BaseModel):
    current_player: Player
    pending_removal: Piece | None
    upcoming_removal: Piece | None
    retained_pieces_after_removal: list[Piece]
    current_winning_moves: list[int]
    opponent_real_threats: list[int]
    explanation: list[str]


class GameState(BaseModel):
    game_id: str
    current_player: Player
    move_number: int = Field(ge=0)
    pieces: list[Piece]
    board: list[Piece | None] = Field(min_length=9, max_length=9)
    status: GameStatus
    winner: Player | None
    winning_line: list[int] | None
    history: list[MoveEvent]
    pending_removal: Piece | None
    upcoming_removal: Piece | None
    legal_moves: list[int]
    analysis: Analysis


class CreateGameRequest(BaseModel):
    first_player: Player = "X"
    draw_mode: DrawMode = "repetition"
    max_moves: int = Field(default=14, ge=14, le=14)


class MoveRequest(BaseModel):
    position: int = Field(ge=1, le=9)
