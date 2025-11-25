from pydantic import BaseModel
from typing import Optional, Tuple


from models.piece import Piece


class Move(BaseModel):
    piece: Piece
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    captured_piece: Optional[Piece] = None
