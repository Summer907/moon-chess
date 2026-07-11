from fastapi.testclient import TestClient

from app.game import GameStore
from app.main import app, store
from app.protection import hard_ai_slots, rate_limiter


client = TestClient(app)


def setup_function() -> None:
    store.clear()
    rate_limiter.clear()


def test_create_rate_limit_returns_retry_headers() -> None:
    responses = [client.post("/api/games") for _ in range(6)]

    assert all(response.status_code == 200 for response in responses[:5])
    limited = responses[5]
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "60"
    assert limited.headers["ratelimit-limit"] == "5"
    assert limited.headers["ratelimit-remaining"] == "0"


def test_game_store_evicts_old_games_for_same_owner() -> None:
    game_store = GameStore(max_games_per_ip=2, max_games=10)

    first = game_store.create(owner_ip="203.0.113.1")
    game_store.create(owner_ip="203.0.113.1")
    third = game_store.create(owner_ip="203.0.113.1")

    assert game_store.get(third.game_id).game_id == third.game_id
    try:
        game_store.get(first.game_id)
    except Exception as exc:
        assert str(exc) == "棋局不存在。"
    else:
        raise AssertionError("最早的同 IP 棋局应被淘汰")


def test_hard_ai_returns_busy_when_all_slots_are_taken() -> None:
    created = client.post("/api/games").json()
    assert hard_ai_slots.acquire(blocking=False)
    try:
        response = client.get(f"/api/games/{created['game_id']}/hint", params={"level": "hard"})
    finally:
        hard_ai_slots.release()

    assert response.status_code == 503
    assert response.headers["retry-after"] == "1"
