import numpy as np
from dataclasses import dataclass

from models.piece import Piece, PieceColor, PieceType


@dataclass(frozen=True)
class BoardConfig:
    SIZE: int = 4
    INITIAL_BOARD_STATE: np.ndarray = np.array(
        [
            [
                Piece(PieceColor.BLACK, PieceType.ROOK),
                Piece(PieceColor.BLACK, PieceType.QUEEN),
                Piece(PieceColor.BLACK, PieceType.KING),
                Piece(PieceColor.BLACK, PieceType.ROOK),
            ],
            [
                Piece(PieceColor.BLACK, PieceType.PAWN),
                Piece(PieceColor.BLACK, PieceType.PAWN),
                Piece(PieceColor.BLACK, PieceType.PAWN),
                Piece(PieceColor.BLACK, PieceType.PAWN),
            ],
            [
                Piece(PieceColor.WHITE, PieceType.PAWN),
                Piece(PieceColor.WHITE, PieceType.PAWN),
                Piece(PieceColor.WHITE, PieceType.PAWN),
                Piece(PieceColor.WHITE, PieceType.PAWN),
            ],
            [
                Piece(PieceColor.WHITE, PieceType.ROOK),
                Piece(PieceColor.WHITE, PieceType.QUEEN),
                Piece(PieceColor.WHITE, PieceType.KING),
                Piece(PieceColor.WHITE, PieceType.ROOK),
            ],
        ],
        dtype=object,
    )
