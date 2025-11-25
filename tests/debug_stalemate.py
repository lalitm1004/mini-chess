import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from models.board import Board
from models.piece import Piece, PieceColor, PieceType


def debug_stalemate_failure():
    print("Debugging Stalemate Failure...")
    # White King at (0,0), Black Rook at (0,3)
    grid = np.full((4, 4), Piece(PieceColor.EMPTY, PieceType.EMPTY), dtype=object)
    grid[0, 0] = Piece(PieceColor.WHITE, PieceType.KING)
    grid[0, 3] = Piece(PieceColor.BLACK, PieceType.ROOK)

    board = Board(grid=grid)
    board.compute_game_state()

    print(f"White Check Status: {board.check_status[PieceColor.WHITE]}")
    print(f"Black Check Status: {board.check_status[PieceColor.BLACK]}")

    print(f"White Valid Moves: {len(board.valid_moves[PieceColor.WHITE])}")
    print(f"Black Valid Moves: {len(board.valid_moves[PieceColor.BLACK])}")

    for move in board.valid_moves[PieceColor.BLACK]:
        print(f"  Black Move: {move.from_pos} -> {move.to_pos}")

    stalemate = (
        board.stalemate_status[PieceColor.WHITE],
        board.stalemate_status[PieceColor.BLACK],
    )
    print(f"Stalemate Status: {stalemate}")


if __name__ == "__main__":
    debug_stalemate_failure()
