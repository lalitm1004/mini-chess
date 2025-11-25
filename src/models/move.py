from dataclasses import dataclass
from typing import Optional, Tuple


from models.piece import Piece


@dataclass
class Move:
    piece: Piece
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    captured_piece: Optional[Piece] = None
