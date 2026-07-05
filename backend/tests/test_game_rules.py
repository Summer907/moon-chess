import pytest

from app.game import GameError, MoonChessGame
from app.models import Piece


OPENING_SIX = [1, 2, 4, 5, 9, 6]


def play(game: MoonChessGame, moves: list[int]):
    state = game.state()
    for position in moves:
        state = game.move(position)
    return state


def game_after_six() -> MoonChessGame:
    game = MoonChessGame()
    play(game, OPENING_SIX)
    return game


def test_first_five_moves_do_not_remove_pieces() -> None:
    game = MoonChessGame()

    for position in OPENING_SIX[:5]:
        state = game.move(position)
        assert state.history[-1].removed_piece is None


def test_sixth_turn_previews_x_first_piece_before_o_places() -> None:
    game = MoonChessGame()
    state = play(game, OPENING_SIX[:5])

    assert state.current_player == "O"
    assert state.pending_removal is None
    assert state.upcoming_removal is not None
    assert state.upcoming_removal.id == "X1"
    assert state.board[0] is not None
    assert state.board[0].id == "X1"


def test_sixth_move_removes_x_first_piece_after_o_places() -> None:
    game = MoonChessGame()
    play(game, OPENING_SIX[:5])

    state = game.move(6)

    assert state.history[-1].removed_piece is not None
    assert state.history[-1].removed_piece.id == "X1"
    assert state.history[-1].placed_piece.id == "O3"
    assert all(piece.id != "X1" for piece in state.pieces)
    assert state.current_player == "X"
    assert state.pending_removal is None


def test_seventh_move_removes_o_first_piece_after_x_places() -> None:
    game = game_after_six()
    assert game.state().upcoming_removal is not None
    assert game.state().upcoming_removal.id == "O1"

    state = game.move(8)

    assert state.history[-1].removed_piece is not None
    assert state.history[-1].removed_piece.id == "O1"
    assert state.history[-1].placed_piece.id == "X4"
    assert all(piece.id != "O1" for piece in state.pieces)


def test_current_player_can_place_on_position_that_just_became_empty() -> None:
    game = game_after_six()

    state = game.move(1)

    assert state.history[-1].placed_piece.position == 1
    assert state.board[0] is not None
    assert state.board[0].id == "X4"


def test_cannot_place_on_position_that_is_still_occupied() -> None:
    game = game_after_six()

    with pytest.raises(GameError, match="位置 2 当前不可落子"):
        game.move(2)


def test_three_in_a_row_wins_immediately_after_placement() -> None:
    game = MoonChessGame()
    play(game, [1, 4, 2, 5])

    state = game.move(3)

    assert state.status == "won"
    assert state.winner == "X"
    assert state.winning_line == [1, 2, 3]
    assert state.history[-1].winner == "X"


def test_win_is_not_checked_before_pending_removal() -> None:
    game = MoonChessGame()
    game.current_player = "X"
    game.pieces = [
        Piece(id="X1", player="X", position=1, order=1),
        Piece(id="X2", player="X", position=2, order=2),
        Piece(id="X3", player="X", position=3, order=3),
        Piece(id="O1", player="O", position=5, order=1),
        Piece(id="O2", player="O", position=6, order=2),
    ]
    state = game.move(4)

    assert state.status == "playing"
    assert state.winner is None
    assert state.history[-1].removed_piece is not None
    assert state.history[-1].removed_piece.id == "X1"


def test_pending_removal_returns_current_players_oldest_piece() -> None:
    game = MoonChessGame()
    state = play(game, OPENING_SIX[:5])

    assert state.pending_removal is None
    assert state.upcoming_removal is not None
    assert state.upcoming_removal.id == "X1"

    state = game.move(6)
    assert state.pending_removal is None
    assert state.upcoming_removal is not None
    assert state.upcoming_removal.id == "O1"


def test_legal_moves_are_computed_after_pending_removal() -> None:
    game = game_after_six()

    state = game.state()

    assert state.pending_removal is None
    assert state.legal_moves == [1, 3, 7, 8]


def test_thirteenth_move_does_not_draw_without_winner() -> None:
    game = MoonChessGame()
    moves = [1, 2, 3, 4, 5, 7, 1, 9, 8, 2, 3, 4, 1]

    state = play(game, moves)

    assert state.move_number == 13
    assert state.status == "playing"
    assert state.winner is None


def test_fourteenth_move_draws_if_no_winner() -> None:
    game = MoonChessGame()
    moves = [1, 2, 3, 4, 5, 7, 1, 9, 8, 2, 3, 4, 1, 5]

    state = play(game, moves)

    assert state.move_number == 14
    assert state.status == "draw"
    assert state.winner is None
    assert state.legal_moves == []


def test_fourteenth_move_win_takes_priority_over_draw() -> None:
    game = MoonChessGame()
    game.current_player = "O"
    game.move_number = 13
    game.pieces = [
        Piece(id="X1", player="X", position=4, order=1),
        Piece(id="X2", player="X", position=5, order=2),
        Piece(id="O1", player="O", position=1, order=1),
        Piece(id="O2", player="O", position=2, order=2),
    ]
    state = game.move(3)

    assert state.move_number == 14
    assert state.status == "won"
    assert state.winner == "O"
    assert state.winning_line == [1, 2, 3]
