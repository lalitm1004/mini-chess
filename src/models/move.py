from dataclasses import dataclass
from typing import Optional, Tuple

from models.piece import Piece


@dataclass
class Move:
    """represents a chess move.

    Attributes:
        piece (Piece): piece being moved
        from_pos (Tuple[int, int]): starting (row, col)
        to_pos (Tuple[int, int]): ending (row, col)
        captured_piece (Optional[Piece]): piece captured by this move
    """

    piece: Piece
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    captured_piece: Optional[Piece] = None
