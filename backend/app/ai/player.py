from __future__ import annotations

from dataclasses import dataclass
import random

from ..game import GameError, MoonChessGame, other_player
from .heuristics import best_by_heuristic, score_moves
from .models import AiLevel, AiMoveEvaluation, AiMoveResponse, AiOutcome, AiReason
from .solver import HardSolver


@dataclass(frozen=True)
class AiDecision:
    move: int
    outcome: AiOutcome
    confidence: str
    reason_codes: list[AiReason]
    evaluated_moves: list[AiMoveEvaluation]


def build_ai_move_response(game: MoonChessGame, level: AiLevel = "medium", seed: int | None = None, auto_apply: bool = True) -> AiMoveResponse:
    if game.status != "playing":
        raise GameError("game_finished")
    if not game.legal_moves():
        raise GameError("no_legal_moves")
    player = game.current_player
    decision = choose_move(game.clone(), level, seed)
    if decision.move not in game.legal_moves():
        raise GameError("ai_illegal_move")
    state = game.move(decision.move) if auto_apply else game.state()
    return AiMoveResponse(state=state, move=decision.move, level=level, player=player, outcome=decision.outcome,
                          confidence=decision.confidence, reason_codes=decision.reason_codes,
                          evaluated_moves=decision.evaluated_moves, applied=auto_apply)


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
    reasons = [AiReason(code="easy_profile")]
    if winning_moves and rng.random() < 0.7:
        move = rng.choice(winning_moves)
        reasons.append(AiReason(code="selected_winning_move", params={"moves": winning_moves, "move": move}))
    elif block_moves and rng.random() < 0.6:
        move = rng.choice(block_moves)
        reasons.append(AiReason(code="blocked_threat", params={"player": other_player(game.current_player), "moves": block_moves, "move": move}))
    else:
        move = rng.choice(legal_moves)
        reasons.append(AiReason(code="random_selected_move", params={"move": move}))
        if winning_moves and move not in winning_moves:
            reasons.append(AiReason(code="missed_winning_move", params={"moves": winning_moves}))
        if block_moves and move not in block_moves:
            reasons.append(AiReason(code="missed_threat", params={"player": other_player(game.current_player), "moves": block_moves}))
    evaluations = [AiMoveEvaluation(move=value, score=None, outcome="win" if value in winning_moves else "unknown", plies=None,
                                    reason_codes=_easy_move_reasons(value, winning_moves, block_moves)) for value in legal_moves]
    return AiDecision(move=move, outcome="win" if move in winning_moves else "unknown", confidence="random", reason_codes=reasons, evaluated_moves=evaluations)


def choose_medium(game: MoonChessGame) -> AiDecision:
    legal_moves = game.legal_moves()
    player = game.current_player
    opponent = other_player(player)
    analysis = game.analysis()
    winning_moves = [move for move in analysis.current_winning_moves if move in legal_moves]
    block_moves = [move for move in analysis.opponent_real_threats if move in legal_moves]
    scored = score_moves(game, legal_moves)
    evaluations = [AiMoveEvaluation(move=item.move, score=item.score, outcome="win" if item.move in winning_moves else "unknown", plies=None, reason_codes=item.reason_codes) for item in scored]
    if winning_moves:
        selected = best_by_heuristic(game, winning_moves)
        reasons = [AiReason(code="selected_winning_move", params={"moves": winning_moves, "move": selected.move})]
    elif block_moves:
        selected = best_by_heuristic(game, block_moves)
        reasons = [AiReason(code="blocked_threat", params={"player": opponent, "moves": block_moves, "move": selected.move})]
    else:
        selected = max(scored, key=lambda item: (item.score, -item.move))
        reasons = [AiReason(code="highest_heuristic_score", params={"move": selected.move})]
    return AiDecision(move=selected.move, outcome="win" if selected.move in winning_moves else "unknown", confidence="heuristic", reason_codes=reasons, evaluated_moves=evaluations)


def choose_hard(game: MoonChessGame) -> AiDecision:
    result, evaluations = HardSolver().evaluate(game)
    if result.move is None:
        raise GameError("no_legal_moves")
    reasons = [AiReason(code="search_selected", params={"move": result.move, "outcome": result.outcome, "plies": result.plies})]
    losing = [item.plies for item in evaluations if item.move != result.move and item.outcome == "loss" and item.plies is not None]
    if losing:
        reasons.append(AiReason(code="other_moves_lose", params={"plies": min(losing)}))
    drawing = [item.move for item in evaluations if item.move != result.move and item.outcome == "draw"]
    if result.outcome == "draw" and drawing:
        reasons.append(AiReason(code="drawing_alternatives", params={"moves": drawing}))
    reasons.append(AiReason(code="optimal_search_move", params={"move": result.move}))
    return AiDecision(move=result.move, outcome=result.outcome, confidence="search", reason_codes=reasons, evaluated_moves=evaluations)


def _easy_move_reasons(move: int, winning_moves: list[int], block_moves: list[int]) -> list[AiReason]:
    if move in winning_moves:
        return [AiReason(code="winning_move")]
    if move in block_moves:
        return [AiReason(code="blocks_real_threat")]
    return [AiReason(code="legal_random_candidate")]
