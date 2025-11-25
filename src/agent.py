from typing import Optional
import math
import random

from models.board import Board
from models.move import Move
from models.piece import PieceColor, PieceType


class MinimaxAgent:
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.color = PieceColor.BLACK

    def get_best_move(self, board: Board) -> Optional[Move]:
        best_move = None
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf

        # get all valid moves for Black
        valid_moves = board.valid_moves[self.color]

        if not valid_moves:
            return None

        # shuffle moves to add some randomness if values are equal
        random.shuffle(valid_moves)

        for move in valid_moves:
            # apply move to get new board state
            new_board = board.apply_move(move)

            # call minimax on the new board
            value = self.minimax(new_board, self.depth - 1, alpha, beta, False)

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        return best_move

    def minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: bool,
    ) -> float:
        if depth == 0:
            return self.evaluate(board)

        # check for game over conditions (checkmate/stalemate)
        # if no moves available for current player
        current_color = self.color if maximizing_player else PieceColor.WHITE
        if not board.valid_moves[current_color]:
            if board.check_status[current_color]:
                # checkmate
                return -math.inf if maximizing_player else math.inf
            else:
                # stalemate
                return 0

        if maximizing_player:
            max_eval = -math.inf
            for move in board.valid_moves[self.color]:
                new_board = board.apply_move(move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in board.valid_moves[PieceColor.WHITE]:
                new_board = board.apply_move(move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, board: Board) -> float:
        # simple material evaluation
        # black is maximizing

        white_score = 0
        black_score = 0

        for r in range(board.size):
            for c in range(board.size):
                piece = board.grid[r, c]
                if piece.piece_type == PieceType.EMPTY:
                    continue

                if piece.piece_color == PieceColor.WHITE:
                    white_score += piece.value
                else:
                    black_score += piece.value

        return black_score - white_score
