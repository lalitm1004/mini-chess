import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from models.board import Board
from models.piece import Piece, PieceColor, PieceType


def test_user_scenario():
    print("Testing User Scenario...")
    # 4|r . . r|  (Row 0)
    # 3|p k p p|  (Row 1)
    # 2|Q P . P|  (Row 2)
    # 1|R . K R|  (Row 3)
    #   a b c d

    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)

    # Row 0
    grid[0, 0] = Piece(PieceColor.BLACK, PieceType.ROOK)
    grid[0, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)

    # Row 1
    grid[1, 0] = Piece(PieceColor.BLACK, PieceType.PAWN)
    grid[1, 1] = Piece(PieceColor.BLACK, PieceType.KING)
    grid[1, 2] = Piece(PieceColor.BLACK, PieceType.PAWN)
    grid[1, 3] = Piece(PieceColor.BLACK, PieceType.PAWN)

    # Row 2
    grid[2, 0] = Piece(PieceColor.WHITE, PieceType.QUEEN)
    grid[2, 1] = Piece(PieceColor.WHITE, PieceType.PAWN)
    grid[2, 3] = Piece(PieceColor.WHITE, PieceType.PAWN)

    # Row 3
    grid[3, 0] = Piece(PieceColor.WHITE, PieceType.ROOK)
    grid[3, 2] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[3, 3] = Piece(PieceColor.WHITE, PieceType.ROOK)

    board = Board(grid=grid)
    board.compute_game_state()

    print(f"Black Check Status: {board.check_status[PieceColor.BLACK]}")
    print(f"Black Valid Moves: {len(board.valid_moves[PieceColor.BLACK])}")

    for move in board.valid_moves[PieceColor.BLACK]:
        print(f"  Move: {move.from_pos} -> {move.to_pos}")

    assert len(board.valid_moves[PieceColor.BLACK]) > 0, "Black should have valid moves"
    print("PASS")


if __name__ == "__main__":
    try:
        test_user_scenario()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
