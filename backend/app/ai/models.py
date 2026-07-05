from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..models import GameState


AiLevel = Literal["easy", "medium", "hard"]
AiOutcome = Literal["win", "draw", "loss", "unknown"]


class AiMoveRequest(BaseModel):
    level: AiLevel = "medium"
    seed: int | None = None
    auto_apply: bool = True


class AiMoveEvaluation(BaseModel):
    move: int = Field(ge=1, le=9)
    score: float | None
    outcome: AiOutcome
    plies: int | None
    reason: str


class AiMoveResponse(BaseModel):
    state: GameState
    move: int = Field(ge=1, le=9)
    level: AiLevel
    outcome: AiOutcome
    confidence: str
    reason: list[str]
    evaluated_moves: list[AiMoveEvaluation]
    applied: bool
