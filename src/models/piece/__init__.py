from enum import Enum
from typing import Dict, Final, List, Tuple

from config import BoardConfig
from models.piece.displacements import (
    pawn_displacements,
    rook_displacements,
    queen_displacements,
    king_displacements,
)


class PieceColor(Enum):
    BLACK = 0
    WHITE = 1
    EMPTY = None


class PieceType(Enum):
    PAWN = 0
    ROOK = 1
    QUEEN = 2
    KING = 3
    EMPTY = None


class Piece:
    def __init__(self, piece_color: PieceColor, piece_type: PieceType) -> None:
        self.piece_color = piece_color
        self.piece_type = piece_type

    @property
    def symbol(self) -> str:
        return UNICODE_PIECES[(self.piece_color, self.piece_type)]

    @property
    def displacements(self) -> List[Tuple[int, int]]:
        key = (self.piece_color, self.piece_type)
        return PIECE_DISPLACEMENTS.get(key, [])

    @property
    def value(self) -> int:
        return PIECE_VALUES[self.piece_type]

    def possible_moves(
        self, position: Tuple[int, int], board_size: int = BoardConfig.SIZE
    ) -> List[Tuple[int, int]]:
        pass

    def __repr__(self) -> str:
        return self.symbol


# Unicode symbols for display
UNICODE_PIECES: Final[Dict[Tuple[PieceColor, PieceType], str]] = {
    (PieceColor.WHITE, PieceType.KING): "♚",
    (PieceColor.WHITE, PieceType.QUEEN): "♛",
    (PieceColor.WHITE, PieceType.ROOK): "♜",
    (PieceColor.WHITE, PieceType.PAWN): "♟",
    (PieceColor.BLACK, PieceType.KING): "♔",
    (PieceColor.BLACK, PieceType.QUEEN): "♕",
    (PieceColor.BLACK, PieceType.ROOK): "♖",
    (PieceColor.BLACK, PieceType.PAWN): "♙",
    (PieceColor.EMPTY, PieceType.EMPTY): ".",
}

PIECE_VALUES: Final[Dict[PieceType, int]] = {
    PieceType.EMPTY: 0,
    PieceType.KING: 1000,
    PieceType.QUEEN: 9,
    PieceType.ROOK: 5,
    PieceType.PAWN: 1,
}

# maximum squares a sliding piece is allowed to move in any given direction
MAX_RANGE = BoardConfig.SIZE - 1

PIECE_DISPLACEMENTS: Final[
    Dict[Tuple[PieceColor, PieceType], List[Tuple[int, int]]]
] = {
    # Pawn
    (PieceColor.WHITE, PieceType.PAWN): pawn_displacements(PieceColor.WHITE),
    (PieceColor.BLACK, PieceType.PAWN): pawn_displacements(PieceColor.BLACK),
    # Rook
    (PieceColor.WHITE, PieceType.ROOK): rook_displacements(MAX_RANGE),
    (PieceColor.BLACK, PieceType.ROOK): rook_displacements(MAX_RANGE),
    # Queen
    (PieceColor.WHITE, PieceType.QUEEN): queen_displacements(MAX_RANGE),
    (PieceColor.BLACK, PieceType.QUEEN): queen_displacements(MAX_RANGE),
    # King
    (PieceColor.WHITE, PieceType.KING): king_displacements(),
    (PieceColor.BLACK, PieceType.KING): king_displacements(),
}
