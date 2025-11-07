from enum import IntEnum
from typing import Dict, Final


# fmt: off
class PieceColor(IntEnum):
    BLACK = 0b000   # 0
    WHITE = 0b100   # 4


class PieceType(IntEnum):
    PAWN  = 0b000    # 0
    ROOK  = 0b001    # 1
    QUEEN = 0b010    # 2
    KING  = 0b011    # 3
# fmt: on

PIECE_TYPE_STR_MAP: Final[Dict[PieceType, str]] = {
    PieceType.PAWN: "P",
    PieceType.ROOK: "R",
    PieceType.QUEEN: "Q",
    PieceType.KING: "K",
}

STR_PIECE_TYPE_MAP: Final[Dict[str, PieceType]] = {
    "P": PieceType.PAWN,
    "R": PieceType.ROOK,
    "Q": PieceType.QUEEN,
    "K": PieceType.KING,
}


class Piece:
    def __init__(self, color: PieceColor, type: PieceType) -> None:
        self.piece_color = color
        self.piece_type = type

    def symbol(self) -> str:
        s = PIECE_TYPE_STR_MAP[self.piece_type]
        return s.lower() if self.piece_color == PieceColor.BLACK else s

    def __repr__(self) -> str:
        return self.symbol()
