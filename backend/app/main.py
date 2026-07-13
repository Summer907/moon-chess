from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ai import AiLevel, AiMoveRequest, AiMoveResponse, build_ai_move_response
from .game import GameError, GameStore
from .models import CreateGameRequest, GameState, MoveRequest
from .protection import ai_slot, client_ip, enforce_rate_limit, settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

app = FastAPI(title="Moon Chess API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = GameStore(
    playing_ttl_seconds=settings.playing_game_ttl_seconds,
    finished_ttl_seconds=settings.finished_game_ttl_seconds,
    max_games_per_ip=settings.max_games_per_ip,
    max_games=settings.max_games,
)


ERROR_STATUS = {
    "game_not_found": 404, "game_finished": 409, "invalid_move": 422,
    "no_legal_moves": 409, "ai_illegal_move": 500, "game_capacity_reached": 503,
}


def game_http_error(exc: GameError) -> HTTPException:
    return HTTPException(status_code=ERROR_STATUS.get(exc.code, 400), detail={"code": exc.code, "params": exc.params})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    fields = [".".join(str(part) for part in item["loc"]) for item in exc.errors()]
    return Response(content=__import__("json").dumps({"detail": {"code": "validation_error", "params": {"fields": fields}}}), status_code=422, media_type="application/json")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/games", response_model=GameState)
def create_game(
    request: Request,
    response: Response,
    payload_request: CreateGameRequest | None = None,
) -> GameState:
    enforce_rate_limit(request, response, "create-minute", settings.create_per_minute, 60)
    enforce_rate_limit(request, response, "create-hour", settings.create_per_hour, 60 * 60)
    payload = payload_request or CreateGameRequest()
    try:
        return store.create(
            first_player=payload.first_player,
            max_moves=payload.max_moves,
            owner_ip=client_ip(request),
        )
    except GameError as exc:
        error = game_http_error(exc)
        error.headers = {"Retry-After": "1"}
        raise error from exc


@app.get("/api/games/{game_id}", response_model=GameState)
def get_game(game_id: str, request: Request, response: Response) -> GameState:
    enforce_rate_limit(request, response, "general", settings.general_per_minute, 60)
    try:
        with store.locked(game_id) as game:
            return game.state()
    except GameError as exc:
        raise game_http_error(exc) from exc


@app.post("/api/games/{game_id}/moves", response_model=GameState)
def make_move(game_id: str, request: MoveRequest, http_request: Request, response: Response) -> GameState:
    enforce_rate_limit(http_request, response, "general", settings.general_per_minute, 60)
    try:
        with store.locked(game_id) as game:
            return game.move(request.position)
    except GameError as exc:
        raise game_http_error(exc) from exc


@app.get("/api/games/{game_id}/hint", response_model=AiMoveResponse)
def get_hint(
    game_id: str,
    request: Request,
    response: Response,
    level: AiLevel = "medium",
    seed: int | None = None,
) -> AiMoveResponse:
    limit = settings.hard_ai_per_minute if level == "hard" else settings.ai_per_minute
    enforce_rate_limit(request, response, f"ai-{level}", limit, 60)
    try:
        with store.locked(game_id) as game:
            snapshot = game.clone()
    except GameError as exc:
        raise game_http_error(exc) from exc
    try:
        with ai_slot(level):
            return build_ai_move_response(snapshot, level=level, seed=seed, auto_apply=False)
    except GameError as exc:
        raise game_http_error(exc) from exc


@app.post("/api/games/{game_id}/ai-move", response_model=AiMoveResponse)
def make_ai_move(
    game_id: str,
    request: AiMoveRequest,
    http_request: Request,
    response: Response,
) -> AiMoveResponse:
    limit = settings.hard_ai_per_minute if request.level == "hard" else settings.ai_per_minute
    enforce_rate_limit(http_request, response, f"ai-{request.level}", limit, 60)
    try:
        with store.locked(game_id) as game:
            with ai_slot(request.level):
                return build_ai_move_response(
                    game,
                    level=request.level,
                    seed=request.seed,
                    auto_apply=request.auto_apply,
                )
    except GameError as exc:
        raise game_http_error(exc) from exc


@app.post("/api/games/{game_id}/undo", response_model=GameState)
def undo(game_id: str, request: Request, response: Response) -> GameState:
    enforce_rate_limit(request, response, "general", settings.general_per_minute, 60)
    try:
        with store.locked(game_id) as game:
            return game.undo()
    except GameError as exc:
        raise game_http_error(exc) from exc


@app.post("/api/games/{game_id}/reset", response_model=GameState)
def reset(game_id: str, request: Request, response: Response) -> GameState:
    enforce_rate_limit(request, response, "general", settings.general_per_minute, 60)
    try:
        with store.locked(game_id) as game:
            return game.reset()
    except GameError as exc:
        raise game_http_error(exc) from exc


if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str = "") -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail={"code": "api_not_found", "params": {}})
    if not FRONTEND_INDEX.is_file():
        raise HTTPException(status_code=404, detail={"code": "frontend_build_missing", "params": {}})

    dist_root = FRONTEND_DIST.resolve()
    requested_path = (FRONTEND_DIST / full_path).resolve()
    try:
        requested_path.relative_to(dist_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "file_not_found", "params": {}}) from exc

    if requested_path.is_file():
        return FileResponse(requested_path)
    return FileResponse(FRONTEND_INDEX)
