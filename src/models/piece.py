from enum import Enum
from typing import Dict, Final, List, Tuple, Set

from config import BoardConfig


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
    ) -> Set[Tuple[int, int]]:
        return {
            (x, y)
            for dx, dy in self.displacements
            if 0 <= (x := position[0] + dx) < board_size
            and 0 <= (y := position[1] + dy) < board_size
        }

    def __repr__(self) -> str:
        return self.symbol


def pawn_displacements(color: PieceColor) -> List[Tuple[int, int]]:
    direction = -1 if color is PieceColor.WHITE else 1
    return [
        (direction, 0),
        (direction, -1),
        (direction, 1),
    ]


def rook_displacements(max_range: int) -> List[Tuple[int, int]]:
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]
    return __ray_displacements(directions, max_range)


def queen_displacements(max_range: int) -> List[Tuple[int, int]]:
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (-1, -1),
        (1, -1),
        (-1, 1),
    ]
    return __ray_displacements(directions, max_range)


def king_displacements() -> List[Tuple[int, int]]:
    return [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]


def __ray_displacements(
    directions: List[Tuple[int, int]], max_range: int
) -> List[Tuple[int, int]]:
    displacements: List[Tuple[int, int]] = []

    for dx, dy in directions:
        for step in range(1, max_range + 1):
            displacements.append((dx * step, dy * step))

    # dict.fromkeys to maintain order
    return list(dict.fromkeys(displacements))


# Unicode symbols for display
UNICODE_PIECES: Final[Dict[Tuple[PieceColor, PieceType], str]] = {
    (PieceColor.WHITE, PieceType.KING): "K",
    (PieceColor.WHITE, PieceType.QUEEN): "Q",
    (PieceColor.WHITE, PieceType.ROOK): "R",
    (PieceColor.WHITE, PieceType.PAWN): "P",
    (PieceColor.BLACK, PieceType.KING): "k",
    (PieceColor.BLACK, PieceType.QUEEN): "q",
    (PieceColor.BLACK, PieceType.ROOK): "r",
    (PieceColor.BLACK, PieceType.PAWN): "p",
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
