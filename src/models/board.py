import numpy as np
from typing import Dict, Final, List, Optional, Tuple

from models.piece import Piece, PieceColor, PieceType
from models.move import Move
from config import BoardConfig


class Board:
    def __init__(
        self,
        grid: np.ndarray = BoardConfig.INITIAL_BOARD_STATE,
        size: int = BoardConfig.SIZE,
    ):
        self.grid = grid
        self.size = size
        self.threatened_pieces_white, self.threatened_pieces_black = (
            self.__get_threatened_pieces()
        )

    def __get_threatened_pieces(self) -> Tuple[List[Piece], List[Piece]]:
        threatened_map: Dict[PieceColor, List[Piece]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: [],
        }

        for r_target in range(self.size):
            for c_target in range(self.size):
                target_piece: Piece = self.grid[r_target, c_target]
                if target_piece.piece_type == PieceType.EMPTY:
                    continue

                for r_attacker in range(self.size):
                    for c_attacker in range(self.size):
                        attacker_piece: Piece = self.grid[r_attacker, c_attacker]
                        if attacker_piece.piece_type == PieceType.EMPTY:
                            continue

                        if target_piece.piece_color == attacker_piece.piece_color:
                            continue

                        move = Move(
                            piece=attacker_piece,
                            from_pos=(r_attacker, c_attacker),
                            to_pos=(r_target, c_target),
                            captured_piece=target_piece,
                        )

                        if self.__is_move_valid(move):
                            threatened_map[target_piece.piece_color].append(
                                target_piece
                            )

        return (
            threatened_map[PieceColor.WHITE],
            threatened_map[PieceColor.BLACK],
        )

    def __is_move_valid(self, move: Move) -> bool:
        r_to, c_to = move.to_pos

        from_piece: Piece = move.piece
        to_piece: Piece = self.grid[r_to, c_to]

        if (
            from_piece.piece_color == to_piece.piece_color
        ):  # target piece color cannot be the same
            return False

        match from_piece.piece_type:
            case PieceType.PAWN:
                return self.__is_move_valid_pawn(move, to_piece)
            case PieceType.ROOK:
                return self.__is_move_valid_rook(move, to_piece)
            case PieceType.QUEEN:
                return self.__is_move_valid_queen(move, to_piece)
            case PieceType.KING:
                return self.__is_move_valid_king(move, to_piece)
            case PieceType.EMPTY:
                return False

    def __is_move_valid_pawn(self, move: Move, to_piece: Piece) -> bool:
        assert move.piece.piece_type == PieceType.PAWN

        piece_color = move.piece.piece_color

        r_to, c_to = move.to_pos
        r_from, c_from = move.from_pos

        possible_moves = move.piece.possible_moves(position=move.from_pos)
        if move.to_pos not in possible_moves:
            return False

        forward = -1 if piece_color == PieceColor.WHITE else 1

        if r_to == (r_from + forward):
            if c_to == c_from:  # straight move
                if to_piece.piece_type == PieceType.EMPTY:
                    return True
            elif c_to != c_from:  # diagonal move
                if (
                    to_piece.piece_type != PieceType.EMPTY
                    and to_piece.piece_color != piece_color
                ):
                    return True

            return False

        return False

    def __is_move_valid_rook(self, move: Move, to_piece: Piece) -> bool:
        assert move.piece.piece_type == PieceType.ROOK

        r_to, c_to = move.to_pos
        r_from, c_from = move.from_pos

        possible_moves = move.piece.possible_moves(position=move.from_pos)
        if move.to_pos not in possible_moves:
            return False

        if r_to == r_from:  # horizontal move
            start_col = min(c_to, c_from)
            end_col = max(c_to, c_from)

            for col in range(start_col + 1, end_col):  # excl of both ends!
                current_pos = (r_from, col)
                current_piece_type: PieceType = self.grid[current_pos].piece_type
                if current_piece_type != PieceType.EMPTY:
                    return False

            return True
        elif c_to == c_from:  # vertical move
            start_row = min(r_to, r_from)
            end_row = max(r_to, r_from)

            for row in range(start_row + 1, end_row):  # excl of both ends!
                current_pos = (row, c_from)
                current_piece_type: PieceType = self.grid[current_pos].piece_type
                if current_piece_type != PieceType.EMPTY:
                    return False

            return True

        return False

    def __is_move_valid_queen(self, move: Move, to_piece: Piece) -> bool: ...

    def __is_move_valid_king(self, move: Move, to_piece: Piece) -> bool: ...
