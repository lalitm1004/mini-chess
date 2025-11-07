from typing import Final, List, Optional
from models.piece import Piece, PieceColor, STR_PIECE_TYPE_MAP


class ChessBoard:
    BOARD_SIZE: Final[int] = 4

    def __init__(self) -> None:
        self.board: List[Optional[Piece]] = [None] * (ChessBoard.BOARD_SIZE**2)

    def pos_to_idx(self, r: int, c: int) -> int:
        return r * ChessBoard.BOARD_SIZE + c

    def from_fen(self, fen: str) -> None:
        rows = fen.split("/")
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                idx = self.pos_to_idx(r, c)

                if ch == ".":
                    self.board[idx] = None
                else:
                    color = PieceColor.WHITE if ch.isupper() else PieceColor.BLACK
                    piece_type = STR_PIECE_TYPE_MAP[ch.upper()]
                    self.board[idx] = Piece(color, type=piece_type)

    def to_fen(self) -> str:
        fen_rows: List[str] = []

        for r in range(ChessBoard.BOARD_SIZE):
            row_str = ""
            for c in range(ChessBoard.BOARD_SIZE):
                piece = self.board[self.pos_to_idx(r, c)]
                row_str += piece.symbol() if piece else "."

            fen_rows.append(row_str)

        return "/".join(fen_rows)

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < ChessBoard.BOARD_SIZE and 0 <= c < ChessBoard.BOARD_SIZE

    def get_piece(self, r: int, c: int) -> Optional[Piece]:
        if not self.in_bounds(r, c):
            return None

        return self.board[self.pos_to_idx(r, c)]

    def set_piece(self, r: int, c: int, piece: Optional[Piece]) -> None:
        if self.in_bounds(r, c):
            self.board[self.pos_to_idx(r, c)] = piece
