import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from models.board import Board
from models.piece import Piece, PieceColor, PieceType


def test_checkmate_detection():
    print("Testing Checkmate Detection...")
    # Fool's Mate setup or similar simple mate
    # White King at (0,0)
    # Black Rook at (0,3) -> attacks row 0
    # Black Rook at (1,3) -> attacks row 1
    # This should be mate.

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)
    grid[0, 0] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[0, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)
    grid[1, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)

    board = Board(grid=grid)

    print(f"White Check Status: {board.check_status[PieceColor.WHITE]}")
    print(f"White Valid Moves: {len(board.valid_moves[PieceColor.WHITE])}")
    for move in board.valid_moves[PieceColor.WHITE]:
        print(f"  Move: {move.from_pos} -> {move.to_pos}")

    is_mate = board.checkmate_status[PieceColor.WHITE]
    print(f"Is Checkmate (White): {is_mate}")

    assert is_mate == True, "Should be checkmate for White"
    print("PASS")


if __name__ == "__main__":
    try:
        test_checkmate_detection()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
