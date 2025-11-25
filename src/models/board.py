import numpy as np
from typing import Dict, List, Optional, Tuple

from config import BoardConfig
from models.piece import Piece, PieceColor, PieceType
from models.move import Move

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
    """represents a chess board and game state.

    Args:
        grid (Optional[np.ndarray]): board state matrix, defaults to initial position
        size (int): board dimensions (4x4 for Silverman chess)
    """

    def __init__(
        self,
        grid: Optional[np.ndarray] = None,
        size: int = BoardConfig.SIZE,
    ):
        self.grid = grid if grid is not None else INITIAL_BOARD_STATE.copy()
        self.size = size

        # initialize empty game state attributes
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
        """compute valid moves and all game state info.

        calculates valid moves for both colors, check status, checkmate,
        stalemate, and threatened pieces. must be called after board
        creation or after applying moves.
        """
        valid_moves_white = self.get_valid_moves_for_color(PieceColor.WHITE)
        valid_moves_black = self.get_valid_moves_for_color(PieceColor.BLACK)

        self.valid_moves = {
            PieceColor.WHITE: valid_moves_white,
            PieceColor.BLACK: valid_moves_black,
        }

        is_check_white = self.is_check(PieceColor.WHITE)
        is_check_black = self.is_check(PieceColor.BLACK)

        self.check_status = {
            PieceColor.WHITE: is_check_white,
            PieceColor.BLACK: is_check_black,
        }

        self.checkmate_status = {
            PieceColor.WHITE: is_check_white and len(valid_moves_white) == 0,
            PieceColor.BLACK: is_check_black and len(valid_moves_black) == 0,
        }

        self.stalemate_status = {
            PieceColor.WHITE: not is_check_white and len(valid_moves_white) == 0,
            PieceColor.BLACK: not is_check_black and len(valid_moves_black) == 0,
        }

        # compute threatened pieces
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
        """get all legal moves for the given color.

        generates pseudo-legal moves based on piece movement rules,
        then filters out moves that would leave own king in check.

        Args:
            color (PieceColor): color to generate moves for

        Returns:
            List[Move]: all legal moves for the color
        """
        moves = []

        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.EMPTY or piece.piece_color != color:
                    continue

                piece_moves = piece.possible_moves(position=(r, c))

                for to_pos in piece_moves:
                    to_r, to_c = to_pos

                    if not self._is_within_bounds(to_r, to_c):
                        continue

                    target: Piece = self.grid[to_r, to_c]

                    if not self._is_valid_piece_move(
                        piece, target, (r, c), (to_r, to_c)
                    ):
                        continue

                    move = Move(piece, (r, c), (to_r, to_c), target)

                    # disallow moves that leave king in check
                    if not self._does_move_leave_king_in_check(move, color):
                        moves.append(move)

        return moves

    def apply_move(self, move: Move) -> "Board":
        """apply a move and return new board state.

        creates a new Board with the move applied. does not modify
        the current board (immutable).

        Args:
            move (Move): move to apply

        Returns:
            Board: new board instance with move applied
        """
        new_grid = self.grid.copy()
        new_grid[move.from_pos] = Piece(PieceColor.EMPTY, PieceType.EMPTY)
        new_grid[move.to_pos] = move.piece
        return Board(new_grid, self.size)

    def is_check(self, color: PieceColor) -> bool:
        """check if the given color's king is in check.

        Args:
            color (PieceColor): color to check

        Returns:
            bool: True if king is under attack
        """
        king_pos = self._find_king_position(color)
        if not king_pos:
            return False
        return self._is_position_threatened(king_pos[0], king_pos[1], color)

    def _is_position_threatened(self, row: int, col: int, by_color: PieceColor) -> bool:
        """check if position is threatened by opposite color.

        Args:
            row (int): row index
            col (int): column index
            by_color (PieceColor): color whose king is on this square

        Returns:
            bool: True if opponent can attack this position
        """
        opponent_color = self._get_opponent_color(by_color)

        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.EMPTY:
                    continue

                if piece.piece_color != opponent_color:
                    continue

                if self._can_attack(r, c, row, col, piece):
                    return True
        return False

    def _can_attack(
        self, from_r: int, from_c: int, to_r: int, to_c: int, piece: Piece
    ) -> bool:
        """check if piece can attack target position.

        Args:
            from_r (int): piece row
            from_c (int): piece column
            to_r (int): target row
            to_c (int): target column
            piece (Piece): attacking piece

        Returns:
            bool: True if piece can attack target
        """
        match piece.piece_type:
            case PieceType.PAWN:
                return self._can_pawn_attack(piece, from_r, from_c, to_r, to_c)
            case PieceType.ROOK:
                return self._can_rook_attack(piece, from_r, from_c, to_r, to_c)
            case PieceType.QUEEN:
                return self._can_queen_attack(piece, from_r, from_c, to_r, to_c)
            case PieceType.KING:
                return self._can_king_attack(piece, from_r, from_c, to_r, to_c)
            case _:
                return False

    def _is_path_clear(self, from_r: int, from_c: int, to_r: int, to_c: int) -> bool:
        """check if path is clear for sliding pieces.

        Args:
            from_r (int): starting row
            from_c (int): starting column
            to_r (int): ending row
            to_c (int): ending column

        Returns:
            bool: True if no pieces block the path
        """
        dr = 0 if to_r == from_r else (1 if to_r > from_r else -1)
        dc = 0 if to_c == from_c else (1 if to_c > from_c else -1)

        r, c = from_r + dr, from_c + dc
        while (r, c) != (to_r, to_c):
            if self.grid[r, c].piece_type != PieceType.EMPTY:
                return False
            r, c = r + dr, c + dc
        return True

    def _is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def _get_opponent_color(self, color: PieceColor) -> PieceColor:
        return PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE

    def _find_king_position(self, color: PieceColor) -> Optional[Tuple[int, int]]:
        """find king position for given color.

        Args:
            color (PieceColor): color of king to find

        Returns:
            Optional[Tuple[int, int]]: (row, col) or None if not found
        """
        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r, c]
                if piece.piece_type == PieceType.KING and piece.piece_color == color:
                    return (r, c)
        return None

    def _is_valid_piece_move(
        self,
        piece: Piece,
        target: Piece,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        """check if move is valid for given piece type.

        Args:
            piece (Piece): moving piece
            target (Piece): piece at destination
            from_pos (Tuple[int, int]): starting position
            to_pos (Tuple[int, int]): ending position

        Returns:
            bool: True if move follows piece rules
        """
        match piece.piece_type:
            case PieceType.PAWN:
                return self._is_valid_pawn_move(piece, target, from_pos, to_pos)
            case PieceType.ROOK:
                return self._is_valid_rook_move(piece, target, from_pos, to_pos)
            case PieceType.QUEEN:
                return self._is_valid_queen_move(piece, target, from_pos, to_pos)
            case PieceType.KING:
                return self._is_valid_king_move(piece, target, from_pos, to_pos)
            case _:
                return False

    def _is_valid_pawn_move(
        self,
        piece: Piece,
        target: Piece,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        from_r, from_c = from_pos
        to_r, to_c = to_pos
        dc = to_c - from_c

        if dc == 0:  # forward
            return target.piece_type == PieceType.EMPTY
        else:  # diagonal
            return (
                target.piece_type != PieceType.EMPTY
                and target.piece_color != piece.piece_color
            )

    def _is_valid_rook_move(
        self,
        piece: Piece,
        target: Piece,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        if target.piece_color == piece.piece_color:
            return False
        return self._is_path_clear(from_pos[0], from_pos[1], to_pos[0], to_pos[1])

    def _is_valid_queen_move(
        self,
        piece: Piece,
        target: Piece,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        if target.piece_color == piece.piece_color:
            return False
        return self._is_path_clear(from_pos[0], from_pos[1], to_pos[0], to_pos[1])

    def _is_valid_king_move(
        self,
        piece: Piece,
        target: Piece,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
    ) -> bool:
        return target.piece_color != piece.piece_color

    def _can_pawn_attack(
        self, piece: Piece, from_r: int, from_c: int, to_r: int, to_c: int
    ) -> bool:
        forward = -1 if piece.piece_color == PieceColor.WHITE else 1
        dr, dc = to_r - from_r, to_c - from_c
        return dr == forward and dc != 0 and abs(dc) == 1

    def _can_rook_attack(
        self, piece: Piece, from_r: int, from_c: int, to_r: int, to_c: int
    ) -> bool:
        possible_moves = piece.possible_moves(position=(from_r, from_c))
        if (to_r, to_c) not in possible_moves:
            return False
        return self._is_path_clear(from_r, from_c, to_r, to_c)

    def _can_queen_attack(
        self, piece: Piece, from_r: int, from_c: int, to_r: int, to_c: int
    ) -> bool:
        possible_moves = piece.possible_moves(position=(from_r, from_c))
        if (to_r, to_c) not in possible_moves:
            return False
        return self._is_path_clear(from_r, from_c, to_r, to_c)

    def _can_king_attack(
        self, piece: Piece, from_r: int, from_c: int, to_r: int, to_c: int
    ) -> bool:
        possible_moves = piece.possible_moves(position=(from_r, from_c))
        return (to_r, to_c) in possible_moves

    def _does_move_leave_king_in_check(self, move: Move, color: PieceColor) -> bool:
        new_board = self.apply_move(move)
        return new_board.is_check(color)
