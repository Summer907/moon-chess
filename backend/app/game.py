from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Lock
import time
from typing import Iterator
from uuid import uuid4

from .models import Analysis, GameState, MoveEvent, Piece, Player


WINNING_LINES: tuple[tuple[int, int, int], ...] = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    (1, 4, 7),
    (2, 5, 8),
    (3, 6, 9),
    (1, 5, 9),
    (3, 5, 7),
)

DRAW_AFTER_MOVES = 14


class GameError(ValueError):
    """A stable API error that never carries presentation text."""

    def __init__(self, code: str, **params: object) -> None:
        self.code = code
        self.params = params
        super().__init__(code)


def other_player(player: Player) -> Player:
    return "O" if player == "X" else "X"


def sorted_player_pieces(pieces: list[Piece], player: Player) -> list[Piece]:
    return sorted((piece for piece in pieces if piece.player == player), key=lambda piece: piece.order)


def winning_line_for(player: Player, pieces: list[Piece]) -> list[int] | None:
    positions = {piece.position for piece in pieces if piece.player == player}
    for line in WINNING_LINES:
        if set(line).issubset(positions):
            return list(line)
    return None


@dataclass
class GameConfig:
    first_player: Player = "X"
    max_moves: int = DRAW_AFTER_MOVES


class MoonChessGame:
    def __init__(
        self,
        game_id: str | None = None,
        first_player: Player = "X",
        max_moves: int = DRAW_AFTER_MOVES,
    ) -> None:
        self.game_id = game_id or str(uuid4())
        self.config = GameConfig(first_player=first_player, max_moves=max_moves)
        self.current_player: Player = first_player
        self.move_number = 0
        self.pieces: list[Piece] = []
        self.status: str = "playing"
        self.winner: Player | None = None
        self.winning_line: list[int] | None = None
        self.history: list[MoveEvent] = []

    def state(self) -> GameState:
        pending = self.pending_removal() if self.status == "playing" else None
        upcoming = self.upcoming_removal() if self.status == "playing" else None
        legal_moves = self.legal_moves() if self.status == "playing" else []
        return GameState(
            game_id=self.game_id,
            current_player=self.current_player,
            move_number=self.move_number,
            pieces=[piece.model_copy() for piece in self._sorted_pieces()],
            board=self.board(),
            status=self.status,  # type: ignore[arg-type]
            winner=self.winner,
            winning_line=self.winning_line,
            history=[event.model_copy(deep=True) for event in self.history],
            pending_removal=pending.model_copy() if pending else None,
            upcoming_removal=upcoming.model_copy() if upcoming else None,
            legal_moves=legal_moves,
            analysis=self.analysis(),
        )

    def clone(self, include_history: bool = True) -> MoonChessGame:
        cloned = MoonChessGame(
            game_id=self.game_id,
            first_player=self.config.first_player,
            max_moves=self.config.max_moves,
        )
        cloned.current_player = self.current_player
        cloned.move_number = self.move_number
        cloned.pieces = [piece.model_copy() for piece in self.pieces] if include_history else list(self.pieces)
        cloned.status = self.status
        cloned.winner = self.winner
        cloned.winning_line = list(self.winning_line) if self.winning_line else None
        cloned.history = [event.model_copy(deep=True) for event in self.history] if include_history else []
        return cloned

    def move(self, position: int) -> GameState:
        if self.status != "playing":
            raise GameError("game_finished")

        player = self.current_player
        pending = self.pending_removal(player)
        pieces_after_removal = self._pieces_without(pending)
        legal_moves = self.legal_moves(player)
        if position not in legal_moves:
            raise GameError("invalid_move", position=position)

        placed_piece = Piece(
            id=f"{player}{self._next_piece_order(player)}",
            player=player,
            position=position,
            order=self._next_piece_order(player),
        )
        self.pieces = pieces_after_removal + [placed_piece]
        self.move_number += 1

        line = winning_line_for(player, self.pieces)
        winner: Player | None = player if line else None
        removed_after_move: Piece | None = None
        if not winner and self.move_number < self.config.max_moves:
            removed_after_move = self._advance_to_next_player()

        removed_piece = pending or removed_after_move
        removal_phase = "before_move" if pending else "after_move" if removed_after_move else None
        event = MoveEvent(
            move_number=self.move_number,
            player=player,
            removed_piece=removed_piece.model_copy() if removed_piece else None,
            placed_piece=placed_piece,
            position=position,
            winner=winner,
            line=line,
            removal_phase=removal_phase,
        )
        self.history.append(event)

        if winner:
            self.status = "won"
            self.winner = winner
            self.winning_line = line
            return self.state()

        if self.move_number >= self.config.max_moves:
            self.status = "draw"

        return self.state()

    def apply_move_for_search(self, position: int) -> None:
        if self.status != "playing":
            raise GameError("game_finished")

        player = self.current_player
        pending = self.pending_removal(player)
        pieces_after_removal = [piece for piece in self.pieces if not pending or piece.id != pending.id]
        occupied = {piece.position for piece in pieces_after_removal}
        if position < 1 or position > 9 or position in occupied:
            raise GameError("invalid_move", position=position)

        next_order = self._next_piece_order(player)
        placed_piece = Piece(
            id=f"{player}{next_order}",
            player=player,
            position=position,
            order=next_order,
        )
        self.pieces = pieces_after_removal + [placed_piece]
        self.move_number += 1

        line = winning_line_for(player, self.pieces)
        if line:
            self.status = "won"
            self.winner = player
            self.winning_line = line
            return

        if self.move_number >= self.config.max_moves:
            self.status = "draw"
            return

        self.current_player = other_player(self.current_player)
        removed_piece = self.pending_removal(self.current_player)
        if removed_piece:
            self.pieces = [piece for piece in self.pieces if piece.id != removed_piece.id]

    def undo(self) -> GameState:
        if not self.history:
            return self.state()
        events = self.history[:-1]
        self._reset_runtime_state()
        for event in events:
            self._replay_event(event)
        return self.state()

    def reset(self) -> GameState:
        self._reset_runtime_state()
        return self.state()

    def board(self) -> list[Piece | None]:
        board: list[Piece | None] = [None for _ in range(9)]
        for piece in self.pieces:
            board[piece.position - 1] = piece.model_copy()
        return board

    def pending_removal(self, player: Player | None = None, pieces: list[Piece] | None = None) -> Piece | None:
        target_player = player or self.current_player
        target_pieces = sorted_player_pieces(pieces or self.pieces, target_player)
        if len(target_pieces) >= 3:
            return target_pieces[0]
        return None

    def upcoming_removal(self) -> Piece | None:
        return self.pending_removal(other_player(self.current_player))

    def legal_moves(self, player: Player | None = None, pieces: list[Piece] | None = None) -> list[int]:
        if self.status != "playing" and pieces is None:
            return []
        target_player = player or self.current_player
        source_pieces = pieces or self.pieces
        pending = self.pending_removal(target_player, source_pieces)
        pieces_after_removal = self._pieces_without(pending, source_pieces)
        occupied = {piece.position for piece in pieces_after_removal}
        return [position for position in range(1, 10) if position not in occupied]

    def winning_moves_for(self, player: Player) -> list[int]:
        return self._winning_moves_for(player)

    def analysis(self) -> Analysis:
        if self.status != "playing":
            return self._finished_analysis()

        pending = self.pending_removal()
        upcoming = self.upcoming_removal()
        retained = sorted_player_pieces(self._pieces_without(pending), self.current_player)
        current_winning_moves = self.winning_moves_for(self.current_player)
        opponent = other_player(self.current_player)
        opponent_real_threats = self.winning_moves_for(opponent)
        return Analysis(
            current_player=self.current_player,
            pending_removal=pending.model_copy() if pending else None,
            upcoming_removal=upcoming.model_copy() if upcoming else None,
            retained_pieces_after_removal=[piece.model_copy() for piece in retained],
            current_winning_moves=current_winning_moves,
            opponent_real_threats=opponent_real_threats,
        )

    def _winning_moves_for(self, player: Player) -> list[int]:
        moves: list[int] = []
        next_order = self._next_piece_order(player)
        for position in self.legal_moves(player):
            pending = self.pending_removal(player)
            simulated = self._pieces_without(pending) + [
                Piece(id=f"{player}{next_order}", player=player, position=position, order=next_order)
            ]
            if winning_line_for(player, simulated):
                moves.append(position)
        return moves

    def _finished_analysis(self) -> Analysis:
        return Analysis(
            current_player=self.current_player,
            pending_removal=None,
            upcoming_removal=None,
            retained_pieces_after_removal=sorted_player_pieces(self.pieces, self.current_player),
            current_winning_moves=[],
            opponent_real_threats=[],
        )

    def _pieces_without(self, removed_piece: Piece | None, pieces: list[Piece] | None = None) -> list[Piece]:
        source_pieces = pieces or self.pieces
        if not removed_piece:
            return [piece.model_copy() for piece in source_pieces]
        return [piece.model_copy() for piece in source_pieces if piece.id != removed_piece.id]

    def _next_piece_order(self, player: Player) -> int:
        active_orders = [piece.order for piece in self.pieces if piece.player == player]
        history_orders = [event.placed_piece.order for event in self.history if event.player == player]
        return max(active_orders + history_orders, default=0) + 1

    def _sorted_pieces(self) -> list[Piece]:
        return sorted(self.pieces, key=lambda piece: (piece.player, piece.order))

    def _advance_to_next_player(self) -> Piece | None:
        self.current_player = other_player(self.current_player)
        removed_piece = self.pending_removal(self.current_player)
        if removed_piece:
            self.pieces = self._pieces_without(removed_piece)
        return removed_piece.model_copy() if removed_piece else None


    def _reset_runtime_state(self) -> None:
        self.current_player = self.config.first_player
        self.move_number = 0
        self.pieces = []
        self.status = "playing"
        self.winner = None
        self.winning_line = None
        self.history = []

    def _replay_event(self, event: MoveEvent) -> None:
        if self.status != "playing":
            return
        self.pieces = self._pieces_without(event.removed_piece) + [event.placed_piece.model_copy()]
        self.move_number = event.move_number
        self.history.append(event.model_copy(deep=True))
        if event.winner:
            self.status = "won"
            self.winner = event.winner
            self.winning_line = event.line
            return
        self.current_player = other_player(event.player)
        if self.move_number >= self.config.max_moves:
            self.status = "draw"


class GameStore:
    def __init__(
        self,
        playing_ttl_seconds: int = 60 * 60,
        finished_ttl_seconds: int = 15 * 60,
        max_games_per_ip: int = 10,
        max_games: int = 5_000,
    ) -> None:
        self._games: dict[str, StoredGame] = {}
        self._playing_ttl_seconds = playing_ttl_seconds
        self._finished_ttl_seconds = finished_ttl_seconds
        self._max_games_per_ip = max_games_per_ip
        self._max_games = max_games
        self._lock = Lock()

    def create(
        self,
        first_player: Player = "X",
        max_moves: int = DRAW_AFTER_MOVES,
        owner_ip: str = "unknown",
    ) -> GameState:
        with self._lock:
            self._prune_locked()
            self._evict_owner_games_locked(owner_ip)
            self._evict_to_capacity_locked()
            if len(self._games) >= self._max_games:
                raise GameError("game_capacity_reached")
            game = MoonChessGame(first_player=first_player, max_moves=max_moves)
            self._games[game.game_id] = StoredGame(game=game, owner_ip=owner_ip)
            return game.state()

    def get(self, game_id: str) -> MoonChessGame:
        with self._lock:
            return self._entry_locked(game_id).game

    @contextmanager
    def locked(self, game_id: str) -> Iterator[MoonChessGame]:
        with self._lock:
            entry = self._entry_locked(game_id)
        with entry.lock:
            with self._lock:
                entry.last_accessed = time.monotonic()
            yield entry.game

    def clear(self) -> None:
        with self._lock:
            self._games.clear()

    def _entry_locked(self, game_id: str) -> StoredGame:
        self._prune_locked()
        try:
            entry = self._games[game_id]
        except KeyError as exc:
            raise GameError("game_not_found") from exc
        entry.last_accessed = time.monotonic()
        return entry

    def _prune_locked(self) -> None:
        now = time.monotonic()
        expired_ids = [
            game_id
            for game_id, entry in self._games.items()
            if now - entry.last_accessed > (
                self._playing_ttl_seconds if entry.game.status == "playing" else self._finished_ttl_seconds
            )
        ]
        for game_id in expired_ids:
            del self._games[game_id]

    def _evict_owner_games_locked(self, owner_ip: str) -> None:
        owner_entries = sorted(
            ((game_id, entry) for game_id, entry in self._games.items() if entry.owner_ip == owner_ip),
            key=lambda item: item[1].last_accessed,
        )
        while len(owner_entries) >= self._max_games_per_ip:
            game_id, _ = owner_entries.pop(0)
            del self._games[game_id]

    def _evict_to_capacity_locked(self) -> None:
        while len(self._games) >= self._max_games:
            oldest_game_id = min(self._games, key=lambda game_id: self._games[game_id].last_accessed)
            del self._games[oldest_game_id]


@dataclass
class StoredGame:
    game: MoonChessGame
    owner_ip: str
    last_accessed: float = field(default_factory=time.monotonic)
    lock: Lock = field(default_factory=Lock)
