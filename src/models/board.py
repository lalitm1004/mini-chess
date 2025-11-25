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

        if from_piece.piece_color == to_piece.piece_color:
            return False

        match from_piece:
            case PieceType.PAWN:
                return self.__is_move_valid_pawn(move, to_piece)
            case PieceType.ROOK:
                return self.__is_move_valid_rook(move, to_piece)
            case PieceType.QUEEN:
                return self.__is_move_valid_queen(move, to_piece)
            case PieceType.KING:
                return self.__is_move_valid_queen(move, to_piece)
            case PieceType.EMPTY:
                return False

    def __is_move_valid_pawn(self, move: Move, to_piece: Piece) -> bool:
        assert move.piece == PieceType.PAWN

        r_from, c_from = move.from_pos

        displacements = move.piece.displacements
        straight_pos = r_from + displacements[0][0], c_from + displacements[0][1]
        diagonal_pos1 = r_from + displacements[1][0], c_from + displacements[1][1]
        diagonal_pos2 = r_from + displacements[2][0], c_from + displacements[2][1]

        # match move.to_pos:
        #     case straight_pos:
        #         pass
        #     case diagonal_pos1:
        #         pass
        #     case diagonal_pos2:
        #         pass
        #     case _:
        #         pass

    def __is_move_valid_rook(self, move: Move, to_piece: Piece) -> bool: ...

    def __is_move_valid_queen(self, move: Move, to_piece: Piece) -> bool: ...

    def __is_move_valid_king(self, move: Move, to_piece: Piece) -> bool: ...
