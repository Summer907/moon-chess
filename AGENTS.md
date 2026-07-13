# Repository Guidelines

## Project Structure & Module Organization

MoonChess is split into a FastAPI backend and a Vue/Vite frontend. Backend source lives in `backend/app/`: `game.py` contains the rule engine, `main.py` exposes the API, `models.py` defines Pydantic schemas, and `ai/` provides AI opponent logic (hint and auto-move). Backend tests are in `backend/tests/`. Frontend source lives in `frontend/src/`, with API calls in `api/`, Vue components in `components/`, views in `views/`, routing and per-route metadata in `router.ts`, shared CSS in `styles/`, TypeScript types in `types/`, browser-side helpers in `utils/`, and i18n setup in `i18n/`. `i18n/` owns the vue-i18n instance, locale detection/persistence, language packs, route-title synchronization, and API error-code translation. Route favicon assets live in the repository-level `assets/` directory. Utility scripts live in `scripts/`, including `scripts/solve_moon_chess.py`.

## Build, Test, and Development Commands

- `uv sync`: create/update the repository-root `.venv` and install all backend and development dependencies.
- `uv run uvicorn --app-dir backend app.main:app --reload --port 8000`: run the local API.
- `uv run pytest -q`: run backend rule tests.
- `cd frontend && npm install`: install frontend dependencies.
- `cd frontend && npm run dev`: start the Vite dev server.
- `cd frontend && npm run build`: run Vue type checking and produce a production build.
- `cd frontend && npm run preview`: preview the production build locally.

The frontend defaults to `VITE_API_BASE_URL=http://localhost:8000`; override it in `frontend/.env` when needed.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints, `snake_case` functions, and explicit model types in Python. Keep rule logic in `backend/app/game.py`; API handlers should stay thin. Use 2-space indentation in Vue and TypeScript, PascalCase for components, and camelCase for refs, functions, and props. User-visible Vue text, ARIA labels, titles, and placeholders must use semantic i18n keys rather than hardcoded strings or string concatenation. No formatter or linter is configured, so match the existing style and keep imports grouped.

## Testing Guidelines

Backend tests use pytest. Name files `test_*.py` and functions `test_*`. Add or update tests whenever rule behavior changes, especially around removals, win priority, legal moves, draws, max-move limits, error codes, and structured AI fields. Run `uv run pytest -q` from the repository root before backend submissions. For frontend changes, run `npm run build`.

## Commit & Pull Request Guidelines

Git history currently uses Conventional Commit style, for example `feat: 实现月亮棋演示程序`. Prefer concise messages like `fix: correct fourteenth-move draw` or `test: add fourteenth-move coverage`. Pull requests should describe behavior changes, list verification commands, link related issues, and include screenshots or short recordings for visible UI changes.

## Architecture Notes

The backend is the source of truth for legal moves, removals, winners, draw state, AI moves, and analysis fields. It returns structured facts and stable error codes, not UI-natural-language strings. The frontend should render API `GameState` and avoid re-deriving fields such as `pending_removal`, `upcoming_removal`, `legal_moves`, `winner`, or threat analysis; it may localize those facts, `removal_phase`, AI `reason_codes`, and API `{ detail: { code, params } }` errors. Do not compare error-message text or restore removed presentation fields such as `note`, `explanation`, or string `reason`.

Python dependencies are managed from the repository root with `uv`; commit both `pyproject.toml` and `uv.lock`. Runtime dependencies belong in `[project.dependencies]`, while test-only dependencies belong in `[dependency-groups].dev`. Do not add or use a Conda environment or `requirements.txt`. Render installs locked production dependencies with `uv sync --locked --no-dev`.

The frontend has three views: `MoonHallView` (route `/`, the mode-selection landing page), `SilverMoonTeaPartyView` (route `/tea-party`, the single-player-vs-AI play view), and `LunarOrbitView` (route `/lunar-orbit`, an analysis/simulation sandbox). The tea-party view currently has no multiplayer mode planned. Keep route `meta.titleKey` values and favicons in `frontend/src/router.ts`; i18n synchronizes titles after route or language changes. Support only `zh-CN` and `en-US`; locale preference uses `localStorage`, while independent game-start settings remain in `utils/useGamePreferences.ts` and `sessionStorage`. Both game views share `ResponsiveDisclosure` for desktop/mobile panels; preserve those shared paths instead of duplicating responsive or storage logic in a view.
