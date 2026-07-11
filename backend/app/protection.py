from __future__ import annotations

from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
import math
import os
from threading import BoundedSemaphore, Lock
import time
from typing import Iterator

from fastapi import HTTPException, Request, Response


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} 必须为正整数。")
    return value


@dataclass(frozen=True)
class ProtectionSettings:
    create_per_minute: int = _positive_int("RATE_LIMIT_CREATE_PER_MINUTE", 5)
    create_per_hour: int = _positive_int("RATE_LIMIT_CREATE_PER_HOUR", 30)
    general_per_minute: int = _positive_int("RATE_LIMIT_GENERAL_PER_MINUTE", 60)
    ai_per_minute: int = _positive_int("RATE_LIMIT_AI_PER_MINUTE", 20)
    hard_ai_per_minute: int = _positive_int("RATE_LIMIT_HARD_AI_PER_MINUTE", 5)
    medium_ai_concurrency: int = _positive_int("AI_STANDARD_CONCURRENCY", 4)
    hard_ai_concurrency: int = _positive_int("AI_HARD_CONCURRENCY", 1)
    playing_game_ttl_seconds: int = _positive_int("GAME_PLAYING_TTL_SECONDS", 60 * 60)
    finished_game_ttl_seconds: int = _positive_int("GAME_FINISHED_TTL_SECONDS", 15 * 60)
    max_games_per_ip: int = _positive_int("MAX_GAMES_PER_IP", 10)
    max_games: int = _positive_int("MAX_GAMES", 5_000)
    trusted_proxy_ips: frozenset[str] = frozenset(
        item.strip() for item in os.getenv("TRUSTED_PROXY_IPS", "").split(",") if item.strip()
    )


settings = ProtectionSettings()


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._last_seen: dict[str, float] = {}
        self._checks = 0
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.monotonic()
        with self._lock:
            self._checks += 1
            self._last_seen[key] = now
            if self._checks % 100 == 0:
                stale_keys = [
                    stale_key for stale_key, last_seen in self._last_seen.items() if now - last_seen > 60 * 60
                ]
                for stale_key in stale_keys:
                    self._last_seen.pop(stale_key, None)
                    self._requests.pop(stale_key, None)

            entries = self._requests[key]
            cutoff = now - window_seconds
            while entries and entries[0] <= cutoff:
                entries.popleft()

            if len(entries) >= limit:
                retry_after = max(1, math.ceil(entries[0] + window_seconds - now))
                return RateLimitResult(False, limit, 0, retry_after)

            entries.append(now)
            reset_after = max(1, math.ceil(entries[0] + window_seconds - now))
            return RateLimitResult(True, limit, limit - len(entries), reset_after)

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()
            self._last_seen.clear()
            self._checks = 0


rate_limiter = SlidingWindowRateLimiter()
standard_ai_slots = BoundedSemaphore(settings.medium_ai_concurrency)
hard_ai_slots = BoundedSemaphore(settings.hard_ai_concurrency)


def client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else "unknown"
    if peer_ip not in settings.trusted_proxy_ips:
        return peer_ip

    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip() or peer_ip
    return request.headers.get("x-real-ip", peer_ip)


def enforce_rate_limit(
    request: Request,
    response: Response,
    category: str,
    limit: int,
    window_seconds: int,
) -> None:
    result = rate_limiter.check(f"{client_ip(request)}:{category}", limit, window_seconds)
    response.headers["RateLimit-Limit"] = str(result.limit)
    response.headers["RateLimit-Remaining"] = str(result.remaining)
    response.headers["RateLimit-Reset"] = str(result.retry_after)
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请在 {result.retry_after} 秒后重试。",
            headers={
                "Retry-After": str(result.retry_after),
                "RateLimit-Limit": str(result.limit),
                "RateLimit-Remaining": "0",
                "RateLimit-Reset": str(result.retry_after),
            },
        )


@contextmanager
def ai_slot(level: str) -> Iterator[None]:
    semaphore = hard_ai_slots if level == "hard" else standard_ai_slots
    if not semaphore.acquire(blocking=False):
        raise HTTPException(
            status_code=503,
            detail="AI 当前繁忙，请稍后重试。",
            headers={"Retry-After": "1"},
        )
    try:
        yield
    finally:
        semaphore.release()
