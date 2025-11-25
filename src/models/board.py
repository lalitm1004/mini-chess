import numpy as np
from typing import Dict, List, Optional, Tuple

from models.piece import Piece, PieceColor, PieceType
from models.move import Move

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


class Board:
    def __init__(
        self,
        grid: Optional[np.ndarray] = None,
        size: int = SIZE,
    ):
        """Initialize board with grid. Does NOT compute game state."""
        self.grid = grid if grid is not None else INITIAL_BOARD_STATE.copy()
        self.size = size

        # Initialize empty game state attributes
        self.valid_moves: Dict[PieceColor, List[Move]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: [],
        }
        self.threatened_pieces: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: [],
        }
        self.threat_scores: Dict[PieceColor, int] = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }
        self.check_status: Dict[PieceColor, bool] = {
            PieceColor.WHITE: False,
            PieceColor.BLACK: False,
        }
        self.checkmate_status: Dict[PieceColor, bool] = {
            PieceColor.WHITE: False,
            PieceColor.BLACK: False,
        }
        self.stalemate_status: Dict[PieceColor, bool] = {
            PieceColor.WHITE: False,
            PieceColor.BLACK: False,
        }

    def compute_game_state(self) -> None:
        """Compute valid moves, check, checkmate, and stalemate status."""
        # Generate valid moves for both colors
        valid_moves_white = self.get_valid_moves_for_color(PieceColor.WHITE)
        valid_moves_black = self.get_valid_moves_for_color(PieceColor.BLACK)

        self.valid_moves = {
            PieceColor.WHITE: valid_moves_white,
            PieceColor.BLACK: valid_moves_black,
        }

        # Compute check status
        is_check_white = self.is_check(PieceColor.WHITE)
        is_check_black = self.is_check(PieceColor.BLACK)

        self.check_status = {
            PieceColor.WHITE: is_check_white,
            PieceColor.BLACK: is_check_black,
        }

        # Compute checkmate and stalemate
        self.checkmate_status = {
            PieceColor.WHITE: is_check_white and len(valid_moves_white) == 0,
            PieceColor.BLACK: is_check_black and len(valid_moves_black) == 0,
        }

        self.stalemate_status = {
            PieceColor.WHITE: not is_check_white and len(valid_moves_white) == 0,
            PieceColor.BLACK: not is_check_black and len(valid_moves_black) == 0,
        }

        # Compute threatened pieces (for compatibility)
        threatened_white_positions = set()
        threatened_black_positions = set()

        for move in valid_moves_white:
            if move.captured_piece.piece_type != PieceType.EMPTY:
                threatened_black_positions.add(move.to_pos)

        for move in valid_moves_black:
            if move.captured_piece.piece_type != PieceType.EMPTY:
                threatened_white_positions.add(move.to_pos)

        self.threatened_pieces = {
            PieceColor.WHITE: [self.grid[pos] for pos in threatened_white_positions],
            PieceColor.BLACK: [self.grid[pos] for pos in threatened_black_positions],
        }

        self.threat_scores = {
            color: sum(piece.value for piece in pieces)
            for color, pieces in self.threatened_pieces.items()
        }

    def get_valid_moves_for_color(self, color: PieceColor) -> List[Move]:
        """Get all valid moves for a given color (temp/main.py logic)."""
        moves = []

        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.EMPTY:
                    continue

                if piece.piece_color != color:
                    continue

                # Get possible moves for this piece
                piece_moves = piece.possible_moves(position=(r, c))

                for to_pos in piece_moves:
                    to_r, to_c = to_pos

                    # Check bounds
                    if not (0 <= to_r < self.size and 0 <= to_c < self.size):
                        continue

                    target = self.grid[to_r, to_c]

                    # Pawn movement rules
                    if piece.piece_type == PieceType.PAWN:
                        dc = to_c - c
                        if dc == 0:  # Forward move
                            if target.piece_type != PieceType.EMPTY:
                                continue
                        else:  # Diagonal capture
                            if target.piece_type == PieceType.EMPTY:
                                continue
                            if target.piece_color == piece.piece_color:
                                continue
                    else:
                        # Can't capture own pieces
                        if target.piece_type != PieceType.EMPTY:
                            if target.piece_color == piece.piece_color:
                                continue

                    # For rooks and queens, check path
                    if piece.piece_type in [PieceType.ROOK, PieceType.QUEEN]:
                        if not self._is_path_clear(r, c, to_r, to_c):
                            continue

                    move = Move(
                        piece,
                        (r, c),
                        (to_r, to_c),
                        target if target.piece_type != PieceType.EMPTY else target,
                    )

                    # Don't allow moves that leave king in check
                    new_board = self.apply_move(move)
                    if not new_board.is_check(color):
                        moves.append(move)

        return moves

    def apply_move(self, move: Move) -> "Board":
        """Return new board state after applying move (temp/main.py logic)."""
        new_grid = self.grid.copy()
        new_grid[move.from_pos] = Piece(PieceColor.EMPTY, PieceType.EMPTY)
        new_grid[move.to_pos] = move.piece
        return Board(new_grid, self.size)

    def is_check(self, color: PieceColor) -> bool:
        """Check if the given side's king is in check (temp/main.py logic)."""
        # Find king position
        king_pos = None
        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.KING and piece.piece_color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        return self._is_position_threatened(king_pos[0], king_pos[1], color)

    def _is_position_threatened(self, row: int, col: int, by_color: PieceColor) -> bool:
        """Check if a position is threatened by the OPPOSITE color."""
        opponent_color = (
            PieceColor.BLACK if by_color == PieceColor.WHITE else PieceColor.WHITE
        )

        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.EMPTY:
                    continue

                if piece.piece_color != opponent_color:
                    continue

                # Check if this piece can attack the target position
                if self._can_attack(r, c, row, col, piece):
                    return True
        return False

    def _can_attack(
        self, from_r: int, from_c: int, to_r: int, to_c: int, piece: Piece
    ) -> bool:
        """Check if a piece can attack a position (temp/main.py logic)."""
        dr, dc = to_r - from_r, to_c - from_c

        # Pawn special case: can only capture diagonally
        if piece.piece_type == PieceType.PAWN:
            forward = -1 if piece.piece_color == PieceColor.WHITE else 1
            return dr == forward and dc != 0 and abs(dc) == 1

        # Check if move is in piece's possible moves
        possible_moves = piece.possible_moves(position=(from_r, from_c))
        if (to_r, to_c) not in possible_moves:
            return False

        # For rook and queen, check if path is clear
        if piece.piece_type in [PieceType.ROOK, PieceType.QUEEN]:
            return self._is_path_clear(from_r, from_c, to_r, to_c)

        return True

    def _is_path_clear(self, from_r: int, from_c: int, to_r: int, to_c: int) -> bool:
        """Check if path is clear for rook/queen movement (temp/main.py logic)."""
        dr = 0 if to_r == from_r else (1 if to_r > from_r else -1)
        dc = 0 if to_c == from_c else (1 if to_c > from_c else -1)

        r, c = from_r + dr, from_c + dc
        while (r, c) != (to_r, to_c):
            if self.grid[r, c].piece_type != PieceType.EMPTY:
                return False
            r, c = r + dr, c + dc
        return True
