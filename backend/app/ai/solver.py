from __future__ import annotations

from dataclasses import dataclass
from collections import OrderedDict
from threading import Lock

from ..game import WINNING_LINES, MoonChessGame, other_player, sorted_player_pieces
from ..protection import _positive_int
from ..models import Player
from .heuristics import score_move
from .models import AiMoveEvaluation, AiOutcome
from .explanations import outcome_text


CompactState = tuple[int, int, Player, tuple[int, ...], tuple[int, ...]]
MemoSignature = CompactState
CycleSignature = tuple[Player, tuple[int, ...], tuple[int, ...]]
_MEMO_CAPACITY = _positive_int("AI_MEMO_CAPACITY", 100_000)
_GLOBAL_MEMO: OrderedDict[MemoSignature, "SearchResult"] = OrderedDict()
_MEMO_LOCK = Lock()


@dataclass(frozen=True)
class SearchResult:
    outcome: AiOutcome
    plies: int
    move: int | None


class HardSolver:
    def __init__(self) -> None:
        self._memo = _GLOBAL_MEMO

    def evaluate(self, game: MoonChessGame) -> tuple[SearchResult, list[AiMoveEvaluation]]:
        state = self._state_from_game(game)
        visiting = frozenset({self._cycle_signature(state)})
        candidates = [self._evaluate_move(state, move, visiting) for move in self._legal_moves(state)]
        if not candidates:
            return SearchResult(outcome="draw", plies=0, move=None), []

        best = self._choose_best(candidates)
        evaluations = [
            AiMoveEvaluation(
                move=result.move or 0,
                score=self._display_score(game, result),
                outcome=result.outcome,
                plies=result.plies,
                reason=f"搜索结果：{outcome_text(result.outcome)}，距离 {result.plies} 手。",
            )
            for result in candidates
            if result.move is not None
        ]
        return best, sorted(evaluations, key=lambda item: item.move)

    def _solve(self, state: CompactState, visiting: frozenset[CycleSignature]) -> SearchResult:
        cycle_key = self._cycle_signature(state)
        if cycle_key in visiting:
            return SearchResult(outcome="draw", plies=0, move=None)

        with _MEMO_LOCK:
            cached = self._memo.get(state)
            if cached is not None:
                self._memo.move_to_end(state)
                return cached

        candidates = [
            self._evaluate_move(state, move, visiting | {cycle_key})
            for move in self._legal_moves(state)
        ]
        if not candidates:
            result = SearchResult(outcome="draw", plies=0, move=None)
        else:
            result = self._choose_best(candidates)

        with _MEMO_LOCK:
            self._memo[state] = result
            self._memo.move_to_end(state)
            while len(self._memo) > _MEMO_CAPACITY:
                self._memo.popitem(last=False)
        return result

    def _evaluate_move(
        self,
        state: CompactState,
        move: int,
        visiting: frozenset[CycleSignature],
    ) -> SearchResult:
        terminal, next_state = self._apply_move(state, move)
        if terminal is not None:
            return SearchResult(outcome=terminal, plies=1, move=move)

        assert next_state is not None
        child = self._solve(next_state, visiting)
        return SearchResult(
            outcome=self._invert(child.outcome),
            plies=child.plies + 1,
            move=move,
        )

    def _choose_best(self, candidates: list[SearchResult]) -> SearchResult:
        return max(candidates, key=self._sort_key)

    def _sort_key(self, result: SearchResult) -> tuple[int, float, float, int]:
        rank = {"loss": 0, "draw": 1, "win": 2}[result.outcome]
        move = result.move or 0
        if result.outcome == "win":
            speed = -float(result.plies)
        elif result.outcome == "loss":
            speed = float(result.plies)
        else:
            speed = 0.0
        return rank, speed, 0.0, -move

    def _display_score(self, game: MoonChessGame, result: SearchResult) -> float:
        move = result.move or 0
        heuristic = score_move(game, move).score if move else 0.0
        if result.outcome == "win":
            return 10000.0 - result.plies + heuristic / 1000
        if result.outcome == "loss":
            return -10000.0 + result.plies + heuristic / 1000
        return heuristic

    def _state_from_game(self, game: MoonChessGame) -> CompactState:
        x_queue, o_queue = self._piece_queues(game)
        return game.config.max_moves, game.move_number, game.current_player, x_queue, o_queue

    def _cycle_signature(self, state: CompactState) -> CycleSignature:
        _, _, player, x_queue, o_queue = state
        return player, x_queue, o_queue

    def _piece_queues(self, game: MoonChessGame) -> tuple[tuple[int, ...], tuple[int, ...]]:
        x_queue = tuple(piece.position for piece in sorted_player_pieces(game.pieces, "X"))
        o_queue = tuple(piece.position for piece in sorted_player_pieces(game.pieces, "O"))
        return x_queue, o_queue

    def _legal_moves(self, state: CompactState) -> list[int]:
        _, _, player, x_queue, o_queue = state
        x_after, o_after = self._remove_pending(player, x_queue, o_queue)
        occupied = set(x_after) | set(o_after)
        return [position for position in range(1, 10) if position not in occupied]

    def _apply_move(self, state: CompactState, move: int) -> tuple[AiOutcome | None, CompactState | None]:
        max_moves, move_number, player, x_queue, o_queue = state
        x_after, o_after = self._remove_pending(player, x_queue, o_queue)
        if player == "X":
            x_after = (*x_after, move)
        else:
            o_after = (*o_after, move)

        if self._has_line(player, x_after, o_after):
            return "win", None

        next_move_number = move_number + 1
        if next_move_number >= max_moves:
            return "draw", None

        next_player = other_player(player)
        next_x, next_o = self._remove_pending(next_player, x_after, o_after)
        return None, (max_moves, next_move_number, next_player, next_x, next_o)

    def _remove_pending(
        self,
        player: Player,
        x_queue: tuple[int, ...],
        o_queue: tuple[int, ...],
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        if player == "X" and len(x_queue) >= 3:
            return x_queue[1:], o_queue
        if player == "O" and len(o_queue) >= 3:
            return x_queue, o_queue[1:]
        return x_queue, o_queue

    def _has_line(self, player: Player, x_queue: tuple[int, ...], o_queue: tuple[int, ...]) -> bool:
        positions = set(x_queue if player == "X" else o_queue)
        return any(set(line).issubset(positions) for line in WINNING_LINES)

    def _invert(self, outcome: AiOutcome) -> AiOutcome:
        if outcome == "win":
            return "loss"
        if outcome == "loss":
            return "win"
        return outcome
