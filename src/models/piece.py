from enum import Enum
from typing import Dict, Final, List, Tuple, Set

from config import BoardConfig


class PieceColor(Enum):
    """piece color enumeration."""

    BLACK = 0
    WHITE = 1
    EMPTY = None


class PieceType(Enum):
    """piece type enumeration."""

    PAWN = 0
    ROOK = 1
    QUEEN = 2
    KING = 3
    EMPTY = None


class Piece:
    """represents a chess piece.

    Args:
        piece_color (PieceColor): color of the piece
        piece_type (PieceType): type of the piece
    """

    def __init__(self, piece_color: PieceColor, piece_type: PieceType) -> None:
        self.piece_color = piece_color
        self.piece_type = piece_type

    @property
    def symbol(self) -> str:
        """unicode symbol for display.

        Returns:
            str: unicode character representing this piece
        """
        return UNICODE_PIECES[(self.piece_color, self.piece_type)]

    @property
    def displacements(self) -> List[Tuple[int, int]]:
        """possible movement displacements for this piece.

        Returns:
            List[Tuple[int, int]]: list of (row_delta, col_delta) tuples
        """
        key = (self.piece_color, self.piece_type)
        return PIECE_DISPLACEMENTS.get(key, [])

    @property
    def value(self) -> int:
        """material value of the piece.

        Returns:
            int: point value for evaluation
        """
        return PIECE_VALUES[self.piece_type]

    def possible_moves(
        self, position: Tuple[int, int], board_size: int = BoardConfig.SIZE
    ) -> Set[Tuple[int, int]]:
        """get all geometrically valid positions this piece can move to.

        Args:
            position (Tuple[int, int]): current (row, col) position
            board_size (int): size of the board

        Returns:
            Set[Tuple[int, int]]: set of (row, col) positions within board bounds
        """
        return {
            (x, y)
            for dx, dy in self.displacements
            if 0 <= (x := position[0] + dx) < board_size
            and 0 <= (y := position[1] + dy) < board_size
        }

    def __repr__(self) -> str:
        return self.symbol


def pawn_displacements(color: PieceColor) -> List[Tuple[int, int]]:
    """generate pawn movement displacements for given color.

    Args:
        color (PieceColor): color of the pawn

    Returns:
        List[Tuple[int, int]]: forward and diagonal displacements
    """
    direction = -1 if color is PieceColor.WHITE else 1
    return [
        (direction, 0),
        (direction, -1),
        (direction, 1),
    ]


def rook_displacements(max_range: int) -> List[Tuple[int, int]]:
    """generate rook movement displacements.

    Args:
        max_range (int): maximum squares in any direction

    Returns:
        List[Tuple[int, int]]: horizontal and vertical displacements
    """
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]
    return __ray_displacements(directions, max_range)


def queen_displacements(max_range: int) -> List[Tuple[int, int]]:
    """generate queen movement displacements.

    Args:
        max_range (int): maximum squares in any direction

    Returns:
        List[Tuple[int, int]]: horizontal, vertical, and diagonal displacements
    """
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
    """generate king movement displacements.

    Returns:
        List[Tuple[int, int]]: all 8 adjacent square displacements
    """
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
    """generate ray displacements for sliding pieces.

    Args:
        directions (List[Tuple[int, int]]): base direction vectors
        max_range (int): maximum distance in each direction

    Returns:
        List[Tuple[int, int]]: all displacements up to max_range
    """
    displacements: List[Tuple[int, int]] = []

    for dx, dy in directions:
        for step in range(1, max_range + 1):
            displacements.append((dx * step, dy * step))

    # maintain order while removing duplicates
    return list(dict.fromkeys(displacements))


# unicode symbols for display
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

# maximum squares a sliding piece can move
MAX_RANGE = BoardConfig.SIZE - 1

PIECE_DISPLACEMENTS: Final[
    Dict[Tuple[PieceColor, PieceType], List[Tuple[int, int]]]
] = {
    (PieceColor.WHITE, PieceType.PAWN): pawn_displacements(PieceColor.WHITE),
    (PieceColor.BLACK, PieceType.PAWN): pawn_displacements(PieceColor.BLACK),
    (PieceColor.WHITE, PieceType.ROOK): rook_displacements(MAX_RANGE),
    (PieceColor.BLACK, PieceType.ROOK): rook_displacements(MAX_RANGE),
    (PieceColor.WHITE, PieceType.QUEEN): queen_displacements(MAX_RANGE),
    (PieceColor.BLACK, PieceType.QUEEN): queen_displacements(MAX_RANGE),
    (PieceColor.WHITE, PieceType.KING): king_displacements(),
    (PieceColor.BLACK, PieceType.KING): king_displacements(),
}
