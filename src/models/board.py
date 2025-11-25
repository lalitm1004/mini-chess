import numpy as np
from typing import Dict, Final, List, Optional, Tuple, Set

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
        (
            valid_moves_white,
            valid_moves_black,
            threatened_pieces_white,
            threatened_pieces_black,
        ) = self.__get_threatened_pieces()

        self.valid_moves = {
            PieceColor.WHITE: valid_moves_white,
            PieceColor.BLACK: valid_moves_black,
        }

        self.threatened_pieces = {
            PieceColor.WHITE: threatened_pieces_white,
            PieceColor.BLACK: threatened_pieces_black,
        }

        self.threat_scores = {
            color: sum(piece.value for piece in pieces)
            for color, pieces in self.threatened_pieces.items()
        }

        is_check_white, is_check_black = self.__is_check()

        self.check_status = {
            PieceColor.WHITE: is_check_white,
            PieceColor.BLACK: is_check_black,
        }

    def __check_all_moves(
        self,
    ) -> Tuple[List[Move], List[Move], List[Piece], List[Piece]]:
        # threatened squares tracked as (row, col)
        threatened_squares: Dict[PieceColor, set[Tuple[int, int]]] = {
            PieceColor.WHITE: set(),
            PieceColor.BLACK: set(),
        }

        valid_moves_map: Dict[PieceColor, List[Move]] = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: [],
        }

        for r_target in range(self.size):
            for c_target in range(self.size):
                target_piece: Piece = self.grid[r_target, c_target]
                if target_piece.piece_type == PieceType.EMPTY:
                    continue

                for r_moving in range(self.size):
                    for c_moving in range(self.size):
                        moving_piece: Piece = self.grid[r_moving, c_moving]
                        if moving_piece.piece_type == PieceType.EMPTY:
                            continue

                        if moving_piece.piece_color == target_piece.piece_color:
                            continue

                        move = Move(
                            piece=moving_piece,
                            from_pos=(r_moving, c_moving),
                            to_pos=(r_target, c_target),
                            captured_piece=target_piece,
                        )

                        is_valid, move = self.__move_properties(move)
                        if not is_valid:
                            continue

                        # store valid move
                        valid_moves_map[moving_piece.piece_color].append(move)

                        # store threatened square
                        threatened_squares[target_piece.piece_color].add(
                            (r_target, c_target)
                        )

        threatened_pieces_white = [
            self.grid[r][c] for (r, c) in threatened_squares[PieceColor.WHITE]
        ]
        threatened_pieces_black = [
            self.grid[r][c] for (r, c) in threatened_squares[PieceColor.BLACK]
        ]

        return (
            valid_moves_map[PieceColor.WHITE],
            valid_moves_map[PieceColor.BLACK],
            threatened_pieces_white,
            threatened_pieces_black,
        )

    def __move_properties(self, move: Move) -> Tuple[bool, Move]:
        r_to, c_to = move.to_pos

        from_piece: Piece = move.piece
        to_piece: Piece = self.grid[r_to, c_to]

        validity = False

        if (
            from_piece.piece_color == to_piece.piece_color
        ):  # target piece color cannot be the same
            validity = False

        match from_piece.piece_type:
            case PieceType.PAWN:
                validity = self.__is_move_valid_pawn(move, to_piece)
            case PieceType.ROOK:
                validity = self.__is_move_valid_rook(move)
            case PieceType.QUEEN:
                validity = self.__is_move_valid_queen(move, to_piece)
            case PieceType.KING:
                validity = self.__is_move_valid_king(move)
            case PieceType.EMPTY:
                validity = False

        if validity:
            move.captured_piece = to_piece

        return validity, move

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

    def __is_move_valid_rook(self, move: Move) -> bool:
        assert move.piece.piece_type == PieceType.ROOK

        r_to, c_to = move.to_pos
        r_from, c_from = move.from_pos

        if move.to_pos == move.from_pos:
            return False

        possible_moves = move.piece.possible_moves(position=move.from_pos)
        if move.to_pos not in possible_moves:
            return False

        return self.__is_path_clear(r_from, c_from, r_to, c_to)

    def __is_move_valid_queen(self, move: Move, to_piece: Piece) -> bool:
        assert move.piece.piece_type == PieceType.QUEEN

        r_to, c_to = move.to_pos
        r_from, c_from = move.from_pos

        possible_moves = move.piece.possible_moves(position=move.from_pos)
        if move.to_pos not in possible_moves:
            return False

        return self.__is_path_clear(r_from, c_from, r_to, c_to)

    def __is_move_valid_king(self, move: Move) -> bool:
        assert move.piece.piece_type == PieceType.KING

        possible_moves = move.piece.possible_moves(position=move.from_pos)
        if move.to_pos not in possible_moves:
            return False

        return True

    def __is_path_clear(self, r_from: int, c_from: int, to_r: int, to_c: int) -> bool:
        dr = 0 if to_r == r_from else (1 if to_r > r_from else -1)
        dc = 0 if to_c == c_from else (1 if to_c > c_from else -1)

        r, c = r_from + dr, c_from + dc

        while (r, c) != (to_r, to_c):
            from_piece: PieceType = self.grid[r, c].piece_type
            if from_piece != PieceType.EMPTY:
                return False

            r, c = r + dr, c + dc

        return True

    def __is_check(self):
        pass
