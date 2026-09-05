import random
import pytest

from app.game import GameError, GameStore, MoonChessGame
from app.ai.solver import HardSolver, _GLOBAL_MEMO


def test_expiry_boundary_and_active_protection(monkeypatch):
    now = [0.0]
    monkeypatch.setattr("app.game.time.monotonic", lambda: now[0])
    store = GameStore(playing_ttl_seconds=10, max_games=1)
    state = store.create()
    with store.pinned(state.game_id):
        now[0] = 11
        with pytest.raises(GameError, match="game_capacity_reached"):
            store.create(owner_ip="another")
        assert store.get(state.game_id)
    now[0] = 21
    with pytest.raises(GameError, match="game_not_found"):
        store.get(state.game_id)


def test_capacity_preserves_playing_games():
    store = GameStore(max_games_per_ip=1)
    first = store.create()
    with pytest.raises(GameError, match="owner_capacity_reached"):
        store.create()
    assert store.get(first.game_id)


def test_explicit_empty_pieces():
    game = MoonChessGame()
    game.move(1)
    assert game.legal_moves(pieces=[]) == list(range(1, 10))
    assert game.pending_removal(pieces=[]) is None
    assert game._pieces_without(None, []) == []


def reference(game):
    """Independent finite-horizon minimax using the public rule engine."""
    candidates = []
    for move in game.legal_moves():
        child = game.clone()
        child.move(move)
        if child.status == "won":
            outcome, plies = "win", 1
        elif child.status == "draw":
            outcome, plies = "draw", 1
        else:
            result = reference(child)
            outcome = {"win": "loss", "loss": "win", "draw": "draw"}[result[0]]
            plies = result[1] + 1
        candidates.append((outcome, plies, move))
    def order(item):
        outcome, plies, move = item
        return {"loss": 0, "draw": 1, "win": 2}[outcome], -plies if outcome == "win" else plies if outcome == "loss" else 0, -move
    return max(candidates, key=order)


@pytest.mark.parametrize("first", ["X", "O"])
def test_search_transition_and_reference(first):
    rng = random.Random(73)
    compared = 0
    for _ in range(30):
        game = MoonChessGame(first_player=first)
        while game.status == "playing":
            move = rng.choice(game.legal_moves())
            fast = game.clone(include_history=False)
            solver = HardSolver()
            terminal, compact = solver._apply_move(solver._state_from_game(game), move)
            fast.apply_move_for_search(move)
            game.move(move)
            assert fast.pieces == game.pieces
            assert fast.status == game.status
            if terminal is None:
                assert compact == solver._state_from_game(game)
            else:
                assert terminal == ("win" if game.status == "won" else "draw")
            if game.status == "playing" and game.move_number == 11 and compared < 4:
                expected = reference(game)
                _GLOBAL_MEMO.clear()
                cold, _ = solver.evaluate(game)
                warm, _ = solver.evaluate(game)
                assert (cold.outcome, cold.plies, cold.move) == expected
                assert cold == warm
                compared += 1
    assert compared > 0
