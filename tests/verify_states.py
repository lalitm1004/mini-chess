import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from models.board import Board
from models.piece import Piece, PieceColor, PieceType


def test_initial_board():
    print("Testing Initial Board...")
    board = Board()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (False, False), f"Initial check failed: {check}"
    assert mate == (False, False), f"Initial mate failed: {mate}"
    assert stalemate == (False, False), f"Initial stalemate failed: {stalemate}"
    print("PASS")


def test_check_white():
    print("Testing White in Check...")
    # White King at (0,0), Black Rook at (0,3)
    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)
    grid[0, 0] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[0, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)

    # Add Black King (safe)
    grid[3, 3] = Piece(PieceColor.BLACK, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (True, False), f"White check failed: {check}"
    assert mate == (False, False), f"White mate failed (should be false): {mate}"
    assert stalemate == (False, False), f"White stalemate failed: {stalemate}"
    print("PASS")


def test_checkmate_white():
    print("Testing White Checkmated...")
    # White King at (0,0)
    # Black Rook at (0,3) -> attacks row 0
    # Black Rook at (1,3) -> attacks row 1
    # This should be mate.

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)
    grid[0, 0] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[0, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)
    grid[1, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)

    # Add Black King (safe)
    grid[3, 3] = Piece(PieceColor.BLACK, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (True, False), f"White checkmate check failed: {check}"
    assert mate == (True, False), f"White checkmate failed: {mate}"
    assert stalemate == (False, False), f"White stalemate failed: {stalemate}"
    print("PASS")


def test_stalemate_white():
    print("Testing White Stalemated...")
    # White King at (0,0)
    # Black Rook at (1,3) -> attacks row 1
    # Black Rook at (2,1) -> attacks col 1
    # King is NOT in check, but cannot move to (0,1), (1,0), (1,1)

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)
    grid[0, 0] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[1, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)  # Attacks row 1
    grid[3, 1] = Piece(PieceColor.BLACK, PieceType.ROOK)  # Attacks col 1

    # Add Black King (safe)
    grid[3, 3] = Piece(PieceColor.BLACK, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (False, False), f"White stalemate check failed: {check}"
    assert mate == (False, False), f"White stalemate mate failed: {mate}"
    assert stalemate == (True, False), f"White stalemate failed: {stalemate}"
    print("PASS")


def test_check_black():
    print("Testing Black in Check...")
    # Black King at (0,0), White Rook at (0,3)

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)

    # Black King
    grid[0, 0] = Piece(PieceColor.BLACK, PieceType.KING)

    # White Rook checking it
    grid[0, 3] = Piece(PieceColor.WHITE, PieceType.ROOK)

    # Add White King (safe)
    grid[3, 3] = Piece(PieceColor.WHITE, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (False, True), f"Black check failed: {check}"
    assert mate == (False, False), f"Black mate failed: {mate}"
    assert stalemate == (False, False), f"Black stalemate failed: {stalemate}"
    print("PASS")


def test_checkmate_black():
    print("Testing Black Checkmated...")
    # Black King at (0,0)
    # White Rook at (0,3) -> attacks row 0
    # White Rook at (1,3) -> attacks row 1

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)

    # Black King
    grid[0, 0] = Piece(PieceColor.BLACK, PieceType.KING)

    # White rooks forming checkmate
    grid[0, 3] = Piece(PieceColor.WHITE, PieceType.ROOK)
    grid[1, 3] = Piece(PieceColor.WHITE, PieceType.ROOK)

    # Add White King (safe)
    grid[3, 3] = Piece(PieceColor.WHITE, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (False, True), f"Black checkmate check failed: {check}"
    assert mate == (False, True), f"Black mate failed: {mate}"
    assert stalemate == (False, False), f"Black stalemate failed: {stalemate}"
    print("PASS")


def test_stalemate_black():
    print("Testing Black Stalemated...")
    # Black King at (0,0)
    # White Rook at (1,3) -> attacks row 1
    # White Rook at (3,1) -> attacks col 1
    # King is NOT in check, but no legal move

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)

    # Black King
    grid[0, 0] = Piece(PieceColor.BLACK, PieceType.KING)

    # White rooks restricting movement
    grid[1, 3] = Piece(PieceColor.WHITE, PieceType.ROOK)
    grid[3, 1] = Piece(PieceColor.WHITE, PieceType.ROOK)

    # Add White King (safe)
    grid[3, 3] = Piece(PieceColor.WHITE, PieceType.KING)

    board = Board(grid=grid)
    board.compute_game_state()

    check = (board.check_status[PieceColor.WHITE], board.check_status[PieceColor.BLACK])
    mate = (
        board.checkmate_status[PieceColor.WHITE],
        board.checkmate_status[PieceColor.BLACK],
    )
    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )

    assert check == (False, False), f"Black stalemate check failed: {check}"
    assert mate == (False, False), f"Black stalemate mate failed: {mate}"
    assert stalemate == (False, True), f"Black stalemate failed: {stalemate}"
    print("PASS")


if __name__ == "__main__":
    try:
        test_initial_board()

        test_check_white()
        test_checkmate_white()
        test_stalemate_white()

        test_check_black()
        test_checkmate_black()
        test_stalemate_black()

        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
