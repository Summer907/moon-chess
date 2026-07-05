from __future__ import annotations

from dataclasses import dataclass

from ..game import WINNING_LINES, MoonChessGame, other_player, sorted_player_pieces
from ..models import Piece, Player


CENTER = 5
CORNERS = {1, 3, 7, 9}
EDGES = {2, 4, 6, 8}


@dataclass(frozen=True)
class HeuristicResult:
    move: int
    score: float
    reason: str


def score_move(game: MoonChessGame, move: int) -> HeuristicResult:
    player = game.current_player
    opponent = other_player(player)
    score = 0.0
    reasons: list[str] = []

    if move == CENTER:
        score += 20
        reasons.append("+20 中心")
    elif move in CORNERS:
        score += 12
        reasons.append("+12 角")
    elif move in EDGES:
        score += 8
        reasons.append("+8 边")

    if creates_future_threat(game, player, move):
        score += 50
        reasons.append("+50 制造真实威胁")

    if keeps_own_pair_aligned(game, player, move):
        score += 30
        reasons.append("+30 自己两子共线")

    if blocks_opponent_pair(game, opponent, move):
        score += 25
        reasons.append("+25 阻断对方共线")

    if move in game.winning_moves_for(opponent):
        score += 10
        reasons.append("+10 占住对手需要点")

    return HeuristicResult(move=move, score=score, reason="，".join(reasons) or "基础合法落子")


def score_moves(game: MoonChessGame, moves: list[int] | None = None) -> list[HeuristicResult]:
    target_moves = moves if moves is not None else game.legal_moves()
    return [score_move(game, move) for move in target_moves]


def best_by_heuristic(game: MoonChessGame, moves: list[int]) -> HeuristicResult:
    scored = score_moves(game, moves)
    return max(scored, key=lambda item: (item.score, -item.move))


def creates_future_threat(game: MoonChessGame, player: Player, move: int) -> bool:
    simulated = game.clone()
    state = simulated.move(move)
    if state.status != "playing":
        return False
    return len(simulated.winning_moves_for(player)) > 0


def keeps_own_pair_aligned(game: MoonChessGame, player: Player, move: int) -> bool:
    own_positions = {piece.position for piece in retained_after_pending(game, player)}
    own_positions.add(move)
    return any(move in line and len(set(line) & own_positions) >= 2 for line in WINNING_LINES)


def blocks_opponent_pair(game: MoonChessGame, opponent: Player, move: int) -> bool:
    opponent_positions = {piece.position for piece in retained_after_pending(game, opponent)}
    return any(move in line and len(set(line) & opponent_positions) >= 2 for line in WINNING_LINES)


def retained_after_pending(game: MoonChessGame, player: Player) -> list[Piece]:
    pending = game.pending_removal(player)
    if not pending:
        return sorted_player_pieces(game.pieces, player)
    return sorted_player_pieces([piece for piece in game.pieces if piece.id != pending.id], player)
