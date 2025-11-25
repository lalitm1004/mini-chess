from typing import List, Tuple

from models.piece import PieceColor


def pawn_displacements(color: PieceColor) -> List[Tuple[int, int]]:
    direction = 1 if color is PieceColor.WHITE else -1
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
