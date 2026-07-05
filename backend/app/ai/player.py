from __future__ import annotations

from dataclasses import dataclass
import random

from ..game import GameError, MoonChessGame, other_player
from .explanations import move_list_text, outcome_text
from .heuristics import best_by_heuristic, score_moves
from .models import AiLevel, AiMoveEvaluation, AiMoveResponse, AiOutcome
from .solver import HardSolver


@dataclass(frozen=True)
class AiDecision:
    move: int
    outcome: AiOutcome
    confidence: str
    reason: list[str]
    evaluated_moves: list[AiMoveEvaluation]


def build_ai_move_response(
    game: MoonChessGame,
    level: AiLevel = "medium",
    seed: int | None = None,
    auto_apply: bool = True,
) -> AiMoveResponse:
    if game.status != "playing":
        raise GameError("棋局已结束，AI 不能继续落子。")
    if not game.legal_moves():
        raise GameError("当前没有合法落子。")

    decision = choose_move(game.clone(), level, seed)
    if decision.move not in game.legal_moves():
        raise GameError("AI 选择了非法落子。")

    state = game.move(decision.move) if auto_apply else game.state()
    return AiMoveResponse(
        state=state,
        move=decision.move,
        level=level,
        outcome=decision.outcome,
        confidence=decision.confidence,
        reason=decision.reason,
        evaluated_moves=decision.evaluated_moves,
        applied=auto_apply,
    )


def choose_move(game: MoonChessGame, level: AiLevel, seed: int | None = None) -> AiDecision:
    if level == "easy":
        return choose_easy(game, seed)
    if level == "medium":
        return choose_medium(game)
    return choose_hard(game)


def choose_easy(game: MoonChessGame, seed: int | None = None) -> AiDecision:
    rng = random.Random(seed)
    legal_moves = game.legal_moves()
    analysis = game.analysis()
    winning_moves = [move for move in analysis.current_winning_moves if move in legal_moves]
    block_moves = [move for move in analysis.opponent_real_threats if move in legal_moves]
    reason = ["简单 AI 会随机犯错。"]

    if winning_moves:
        if rng.random() < 0.7:
            move = rng.choice(winning_moves)
            reason.append(f"当前存在直接胜点 {move_list_text(winning_moves)}，本次选择胜点 {move}。")
        else:
            move = rng.choice(legal_moves)
            if move in winning_moves:
                reason.append(f"当前存在直接胜点 {move_list_text(winning_moves)}，随机仍落在胜点 {move}。")
            else:
                reason.append(f"当前存在直接胜点 {move_list_text(winning_moves)}，但 easy AI 本次没有选择最优落子。")
                reason.append(f"随机选择落在 {move}。")
    elif block_moves:
        opponent = other_player(game.current_player)
        if rng.random() < 0.6:
            move = rng.choice(block_moves)
            reason.append(f"{opponent} 下一回合的真实威胁是 {move_list_text(block_moves)}，本次选择堵 {move}。")
        else:
            move = rng.choice(legal_moves)
            if move in block_moves:
                reason.append(f"{opponent} 有真实威胁，随机仍堵在 {move}。")
            else:
                reason.append(f"{opponent} 有真实威胁，但 easy AI 本次漏防。")
                reason.append(f"随机选择落在 {move}。")
    else:
        move = rng.choice(legal_moves)
        reason.append(f"没有明显胜点或必须防守点，随机选择落在 {move}。")

    evaluations = [
        AiMoveEvaluation(
            move=move_value,
            score=None,
            outcome="win" if move_value in winning_moves else "unknown",
            plies=None,
            reason=_easy_move_reason(move_value, winning_moves, block_moves),
        )
        for move_value in legal_moves
    ]
    return AiDecision(
        move=move,
        outcome="win" if move in winning_moves else "unknown",
        confidence="随机",
        reason=reason,
        evaluated_moves=evaluations,
    )


def choose_medium(game: MoonChessGame) -> AiDecision:
    legal_moves = game.legal_moves()
    player = game.current_player
    opponent = other_player(player)
    analysis = game.analysis()
    winning_moves = [move for move in analysis.current_winning_moves if move in legal_moves]
    block_moves = [move for move in analysis.opponent_real_threats if move in legal_moves]
    scored = score_moves(game, legal_moves)
    evaluations = [
        AiMoveEvaluation(
            move=item.move,
            score=item.score,
            outcome="win" if item.move in winning_moves else "unknown",
            plies=None,
            reason=item.reason,
        )
        for item in scored
    ]

    if winning_moves:
        selected = best_by_heuristic(game, winning_moves)
        return AiDecision(
            move=selected.move,
            outcome="win",
            confidence="启发式",
            reason=[
                f"{player} 当前直接胜点是 {move_list_text(winning_moves)}。",
                f"选择 {selected.move}。",
            ],
            evaluated_moves=evaluations,
        )

    if block_moves:
        selected = best_by_heuristic(game, block_moves)
        return AiDecision(
            move=selected.move,
            outcome="unknown",
            confidence="启发式",
            reason=[
                f"{player} 当前没有直接胜点。",
                f"{opponent} 下一回合的真实威胁是 {move_list_text(block_moves)}，必须堵。",
                f"选择 {selected.move}。",
            ],
            evaluated_moves=evaluations,
        )

    selected = max(scored, key=lambda item: (item.score, -item.move))
    return AiDecision(
        move=selected.move,
        outcome="unknown",
        confidence="启发式",
        reason=[
            f"{player} 当前没有直接胜点。",
            f"{opponent} 下一回合没有真实威胁。",
            f"启发式评分最高的是 {selected.move}：{selected.reason}。",
        ],
        evaluated_moves=evaluations,
    )


def choose_hard(game: MoonChessGame) -> AiDecision:
    result, evaluations = HardSolver().evaluate(game)
    if result.move is None:
        raise GameError("当前没有合法落子。")

    return AiDecision(
        move=result.move,
        outcome=result.outcome,
        confidence="搜索",
        reason=_hard_reason(result.move, result.outcome, result.plies, evaluations),
        evaluated_moves=evaluations,
    )


def _easy_move_reason(move: int, winning_moves: list[int], block_moves: list[int]) -> str:
    if move in winning_moves:
        return "直接胜点"
    if move in block_moves:
        return "可堵对手威胁"
    return "合法随机候选"


def _hard_reason(
    move: int,
    outcome: AiOutcome,
    plies: int,
    evaluations: list[AiMoveEvaluation],
) -> list[str]:
    lines = [f"搜索结果显示，落在 {move} 可以得到{outcome_text(outcome)}。"]
    losing_moves = [item for item in evaluations if item.move != move and item.outcome == "loss"]
    if losing_moves:
        fastest = min(item.plies for item in losing_moves if item.plies is not None)
        lines.append(f"其他部分落子会在 {fastest} 手内导致失败。")
    drawing_moves = [item.move for item in evaluations if item.move != move and item.outcome == "draw"]
    if outcome == "draw" and drawing_moves:
        lines.append(f"另有和棋候选：{move_list_text(drawing_moves)}。")
    lines.append(f"困难 AI 选择理论结果最优的落子 {move}。")
    return lines
