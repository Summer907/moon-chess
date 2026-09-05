from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest

from fastapi.testclient import TestClient

from app import main
from app.game import MoonChessGame
from app.protection import rate_limiter


def test_revision_survives_undo_reset_and_stale_move() -> None:
    rate_limiter.clear()
    client = TestClient(main.app)
    state = client.post("/api/games").json()
    path = f"/api/games/{state['game_id']}"
    for position in [1, 4]:
        state = client.post(path + "/moves", json={"position": position, "expected_revision": state["revision"]}).json()
    response = client.post(path + "/undo", json={"steps": 2, "expected_revision": 2})
    assert response.json()["move_number"] == 0
    assert response.json()["revision"] == 3
    assert client.post(path + "/moves", json={"position": 2, "expected_revision": 2}).status_code == 409
    assert client.post(path + "/reset", json={"expected_revision": 3}).json()["revision"] == 4
    assert client.post(path + "/undo", json={"steps": 3}).status_code == 422


@pytest.mark.parametrize("operation", ["reset", "undo"])
def test_old_ai_cannot_commit_after_reset_or_undo(monkeypatch, operation) -> None:
    rate_limiter.clear()
    client = TestClient(main.app)
    state = client.post("/api/games").json()
    path = f"/api/games/{state['game_id']}"
    entered, release = Event(), Event()
    original = main.build_ai_move_response

    def delayed(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return original(*args, **kwargs)

    monkeypatch.setattr(main, "build_ai_move_response", delayed)
    with ThreadPoolExecutor() as executor:
        future = executor.submit(client.post, path + "/ai-move", json={"level": "easy"})
        assert entered.wait(5)
        try:
            assert client.post(path + "/" + operation).status_code == 200
        finally:
            release.set()
        assert future.result().status_code == 409
    assert client.get(path).json()["move_number"] == 0


def test_atomic_undo_matches_replayed_position() -> None:
    game = MoonChessGame()
    for position in [1, 4, 2, 5, 9, 6]:
        if game.status == "playing":
            game.move(position)
    target = game.history[:-2]
    expected = MoonChessGame()
    for event in target:
        expected.move(event.position)
    revision = game.revision
    state = game.undo(2)
    assert state.board == expected.state().board
    assert state.analysis == expected.state().analysis
    assert state.revision == revision + 1
