from __future__ import annotations

from functools import lru_cache


Player = str
State = tuple[int, Player, tuple[int, ...], tuple[int, ...]]
Outcome = int
MoveResult = tuple[int, Outcome | None, State | None, tuple[int, int, int] | None]

POSITIONS = tuple(range(1, 10))
MAX_MOVES = 14
LINES = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    (1, 4, 7),
    (2, 5, 8),
    (3, 6, 9),
    (1, 5, 9),
    (3, 5, 7),
)


def other(player: Player) -> Player:
    return "O" if player == "X" else "X"


def outcome_text(outcome: Outcome) -> str:
    return {1: "X win", 0: "draw", -1: "O win"}[outcome]


def has_line(player: Player, x_pieces: tuple[int, ...], o_pieces: tuple[int, ...]) -> tuple[int, int, int] | None:
    positions = set(x_pieces if player == "X" else o_pieces)
    for line in LINES:
        if set(line) <= positions:
            return line
    return None


def normalize_after_switch(move_number: int, next_player: Player, x_pieces: tuple[int, ...], o_pieces: tuple[int, ...]) -> State:
    x = x_pieces
    o = o_pieces
    if next_player == "X" and len(x) >= 3:
        x = x[1:]
    if next_player == "O" and len(o) >= 3:
        o = o[1:]
    return move_number, next_player, x, o


def legal_moves(state: State) -> list[int]:
    _, _, x_pieces, o_pieces = state
    occupied = set(x_pieces) | set(o_pieces)
    return [position for position in POSITIONS if position not in occupied]


def apply_move(state: State, position: int) -> tuple[Outcome | None, State | None, tuple[int, int, int] | None]:
    move_number, player, x_pieces, o_pieces = state
    next_move_number = move_number + 1
    x = tuple((*x_pieces, position)) if player == "X" else x_pieces
    o = tuple((*o_pieces, position)) if player == "O" else o_pieces

    line = has_line(player, x, o)
    if line:
        return 1 if player == "X" else -1, None, line
    if next_move_number >= MAX_MOVES:
        return 0, None, None
    return None, normalize_after_switch(next_move_number, other(player), x, o), None


def moves_from(state: State) -> list[MoveResult]:
    return [(position, *apply_move(state, position)) for position in legal_moves(state)]


@lru_cache(maxsize=None)
def solve(state: State) -> tuple[Outcome, int]:
    move_number, player, _, _ = state
    if move_number >= MAX_MOVES:
        return 0, 0

    candidates: list[tuple[int, Outcome, int, State | None, tuple[int, int, int] | None]] = []
    for position, terminal, next_state, line in moves_from(state):
        if terminal is not None:
            outcome = terminal
            distance = 1
        else:
            assert next_state is not None
            outcome, child_distance = solve(next_state)
            distance = child_distance + 1
        candidates.append((position, outcome, distance, next_state, line))

    if player == "X":
        best_outcome = max(candidate[1] for candidate in candidates)
    else:
        best_outcome = min(candidate[1] for candidate in candidates)

    best = [candidate for candidate in candidates if candidate[1] == best_outcome]
    if best_outcome == 0:
        chosen = min(best, key=lambda candidate: (candidate[2], candidate[0]))
    elif best_outcome == 1 and player == "X":
        chosen = min(best, key=lambda candidate: (candidate[2], candidate[0]))
    elif best_outcome == -1 and player == "O":
        chosen = min(best, key=lambda candidate: (candidate[2], candidate[0]))
    else:
        chosen = max(best, key=lambda candidate: (candidate[2], -candidate[0]))
    return chosen[1], chosen[2]


def choose_optimal(state: State) -> MoveResult:
    player = state[1]
    candidates: list[tuple[MoveResult, Outcome, int]] = []
    for result in moves_from(state):
        _, terminal, next_state, _ = result
        if terminal is not None:
            outcome = terminal
            distance = 1
        else:
            assert next_state is not None
            outcome, child_distance = solve(next_state)
            distance = child_distance + 1
        candidates.append((result, outcome, distance))

    if player == "X":
        best_outcome = max(candidate[1] for candidate in candidates)
    else:
        best_outcome = min(candidate[1] for candidate in candidates)

    best = [candidate for candidate in candidates if candidate[1] == best_outcome]
    if best_outcome == 0:
        return min(best, key=lambda candidate: (candidate[2], candidate[0][0]))[0]
    if best_outcome == 1 and player == "X":
        return min(best, key=lambda candidate: (candidate[2], candidate[0][0]))[0]
    if best_outcome == -1 and player == "O":
        return min(best, key=lambda candidate: (candidate[2], candidate[0][0]))[0]
    return max(best, key=lambda candidate: (candidate[2], -candidate[0][0]))[0]


def reachable_states(initial: State) -> set[State]:
    states: set[State] = set()

    def visit(state: State) -> None:
        if state in states:
            return
        states.add(state)
        for _, terminal, next_state, _ in moves_from(state):
            if terminal is None and next_state is not None:
                visit(next_state)

    visit(initial)
    return states


def main() -> None:
    initial: State = (0, "X", (), ())
    states = reachable_states(initial)
    initial_outcome, initial_distance = solve(initial)

    print(f"rule: draw after move {MAX_MOVES} if no winner")
    print(f"initial: {outcome_text(initial_outcome)}, distance={initial_distance}")
    print(f"reachable non-terminal states: {len(states)}")
    print(
        "state values: "
        f"X win={sum(1 for state in states if solve(state)[0] == 1)}, "
        f"O win={sum(1 for state in states if solve(state)[0] == -1)}, "
        f"draw={sum(1 for state in states if solve(state)[0] == 0)}"
    )

    print("\nfirst move outcomes:")
    for position, terminal, next_state, _ in moves_from(initial):
        if terminal is not None:
            outcome = terminal
            distance = 1
        else:
            assert next_state is not None
            outcome, child_distance = solve(next_state)
            distance = child_distance + 1
        print(f"  X{position}: {outcome_text(outcome)}, distance={distance}")

    print("\nrepresentative second-player replies:")
    for first in (1, 2, 5):
        _, _, state_after_first, _ = next(result for result in moves_from(initial) if result[0] == first)
        assert state_after_first is not None
        print(f"  after X{first}:")
        for position, terminal, next_state, _ in moves_from(state_after_first):
            if terminal is not None:
                outcome = terminal
                distance = 1
            else:
                assert next_state is not None
                outcome, child_distance = solve(next_state)
                distance = child_distance + 1
            print(f"    O{position}: {outcome_text(outcome)}, distance={distance}")

    print("\none optimal line:")
    state: State | None = initial
    while state is not None:
        move_number, player, x_pieces, o_pieces = state
        position, terminal, next_state, line = choose_optimal(state)
        if terminal is not None:
            outcome = terminal
            distance = 1
        else:
            assert next_state is not None
            outcome, child_distance = solve(next_state)
            distance = child_distance + 1
        print(
            f"  {move_number + 1:02d}. {player}{position} -> {outcome_text(outcome)}, "
            f"before X={x_pieces} O={o_pieces}, line={line}, distance={distance}"
        )
        state = next_state


if __name__ == "__main__":
    main()
