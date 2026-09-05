"""Run from the repository root: uv run python scripts/benchmark_ai.py."""
import json
from pathlib import Path
import sys
import time
import random

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.game import MoonChessGame
from app.ai.solver import HardSolver, _GLOBAL_MEMO


def main():
    rng = random.Random(17)
    positions = {0: MoonChessGame()}
    while 11 not in positions:
        game = MoonChessGame()
        while game.status == "playing":
            game.move(rng.choice(game.legal_moves()))
            if game.status == "playing" and game.move_number in (6, 11):
                positions[game.move_number] = game.clone()
    rows = []
    for number, game in sorted(positions.items()):
        _GLOBAL_MEMO.clear()
        for temperature in ("cold", "warm"):
            solver = HardSolver()
            start = time.perf_counter()
            result, _ = solver.evaluate(game)
            rows.append(dict(move_number=number, cache=temperature, seconds=round(time.perf_counter()-start, 6),
                             nodes=solver.nodes, hits=solver.hits, outcome=result.outcome, plies=result.plies))
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
