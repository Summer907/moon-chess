from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from ..models import GameState


AiLevel = Literal["easy", "medium", "hard"]
AiOutcome = Literal["win", "draw", "loss", "unknown"]
AiConfidence = Literal["random", "heuristic", "search"]


class AiReason(BaseModel):
    code: str
    params: dict[str, Any] = Field(default_factory=dict)


class AiMoveRequest(BaseModel):
    level: AiLevel = "medium"
    seed: int | None = None
    auto_apply: bool = True


class AiMoveEvaluation(BaseModel):
    move: int = Field(ge=1, le=9)
    score: float | None
    outcome: AiOutcome
    plies: int | None
    reason_codes: list[AiReason]


class AiMoveResponse(BaseModel):
    state: GameState
    move: int = Field(ge=1, le=9)
    level: AiLevel
    outcome: AiOutcome
    player: Literal["X", "O"]
    confidence: AiConfidence
    reason_codes: list[AiReason]
    evaluated_moves: list[AiMoveEvaluation]
    applied: bool
