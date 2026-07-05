# Repository Guidelines

## Project Structure & Module Organization

MoonChess is split into a FastAPI backend and a Vue/Vite frontend. Backend source lives in `backend/app/`: `game.py` contains the rule engine, `main.py` exposes the API, and `models.py` defines Pydantic schemas. Backend tests are in `backend/tests/`. Frontend source lives in `frontend/src/`, with API calls in `api/`, Vue components in `components/`, shared CSS in `styles/`, and TypeScript types in `types/`. Utility scripts live in `scripts/`, including `scripts/solve_moon_chess.py`.

## Build, Test, and Development Commands

- `cd backend && python -m pip install -r requirements.txt`: install backend dependencies.
- `cd backend && python -m uvicorn app.main:app --reload --port 8000`: run the local API.
- `cd backend && python -m pytest -q`: run backend rule tests.
- `cd frontend && npm install`: install frontend dependencies.
- `cd frontend && npm run dev`: start the Vite dev server.
- `cd frontend && npm run build`: run Vue type checking and produce a production build.
- `cd frontend && npm run preview`: preview the production build locally.

The frontend defaults to `VITE_API_BASE_URL=http://localhost:8000`; override it in `frontend/.env` when needed.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints, `snake_case` functions, and explicit model types in Python. Keep rule logic in `backend/app/game.py`; API handlers should stay thin. Use 2-space indentation in Vue and TypeScript, PascalCase for components, and camelCase for refs, functions, and props. No formatter or linter is configured, so match the existing style and keep imports grouped.

## Testing Guidelines

Backend tests use pytest. Name files `test_*.py` and functions `test_*`. Add or update tests whenever rule behavior changes, especially around removals, win priority, legal moves, draws, and max-move limits. Run `python -m pytest -q` from `backend/` before backend submissions. For frontend changes, run `npm run build`.

## Commit & Pull Request Guidelines

Git history currently uses Conventional Commit style, for example `feat: 实现月亮棋演示程序`. Prefer concise messages like `fix: correct fourteenth-move draw` or `test: add fourteenth-move coverage`. Pull requests should describe behavior changes, list verification commands, link related issues, and include screenshots or short recordings for visible UI changes.

## Architecture Notes

The backend is the source of truth for legal moves, removals, winners, draw state, and analysis fields. The frontend should render API `GameState` and avoid re-deriving fields such as `pending_removal`, `upcoming_removal`, `legal_moves`, `winner`, or threat analysis.
