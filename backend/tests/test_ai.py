from fastapi.testclient import TestClient

from app.ai.player import choose_move
from app.game import MoonChessGame
from app.main import app, store


client = TestClient(app)


def play(game: MoonChessGame, moves: list[int]) -> None:
    for move in moves:
        game.move(move)


def test_easy_seed_is_reproducible_and_legal() -> None:
    first = choose_move(MoonChessGame(), "easy", seed=42)
    second = choose_move(MoonChessGame(), "easy", seed=42)

    assert first.move == second.move
    assert first.move in range(1, 10)
    assert len(first.evaluated_moves) == 9


def test_medium_takes_immediate_win() -> None:
    game = MoonChessGame()
    play(game, [1, 4, 2, 5])

    decision = choose_move(game, "medium")

    assert decision.move == 3
    assert decision.outcome == "win"


def test_medium_blocks_real_threat() -> None:
    game = MoonChessGame()
    play(game, [1, 4, 2])

    decision = choose_move(game, "medium")

    assert decision.move == 3
    assert decision.outcome == "unknown"


def test_hard_search_does_not_mutate_game() -> None:
    game = MoonChessGame()

    decision = choose_move(game, "hard")

    assert decision.move in game.legal_moves()
    assert decision.outcome == "draw"
    assert game.move_number == 0
    assert game.history == []
    assert game.pieces == []


def test_hint_does_not_apply_move() -> None:
    store.clear()
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    response = client.get(f"/api/games/{game_id}/hint", params={"level": "medium"})

    assert response.status_code == 200
    body = response.json()
    assert body["applied"] is False
    assert body["state"]["move_number"] == 0
    assert store.get(game_id).state().move_number == 0
    assert body["move"] in created["legal_moves"]


def test_ai_move_applies_move() -> None:
    store.clear()
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    response = client.post(f"/api/games/{game_id}/ai-move", json={"level": "medium"})

    assert response.status_code == 200
    body = response.json()
    assert body["applied"] is True
    assert body["state"]["move_number"] == 1
    assert store.get(game_id).state().move_number == 1
    assert body["move"] in created["legal_moves"]


def test_ai_rejects_finished_game() -> None:
    store.clear()
    created = client.post("/api/games").json()
    game_id = created["game_id"]
    for move in [1, 4, 2, 5, 3]:
        client.post(f"/api/games/{game_id}/moves", json={"position": move})

    response = client.get(f"/api/games/{game_id}/hint", params={"level": "medium"})

    assert response.status_code == 400
