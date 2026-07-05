from __future__ import annotations

from .models import AiOutcome


def move_list_text(moves: list[int]) -> str:
    return "、".join(str(move) for move in moves) if moves else "无"


def outcome_text(outcome: AiOutcome) -> str:
    labels: dict[AiOutcome, str] = {
        "win": "胜",
        "draw": "和棋",
        "loss": "负",
        "unknown": "未知",
    }
    return labels[outcome]
