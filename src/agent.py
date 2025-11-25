from typing import Optional
import math
import random

from models.board import Board
from models.move import Move
from models.piece import PieceColor, PieceType, Piece


class MinimaxAgent:
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.color: PieceColor = PieceColor.BLACK

    def evaluate(self, board: Board):
        scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,  # maximize
        }

        for r in range(board.size):
            for c in range(board.size):
                piece: Piece = board.grid[r, c]
                if piece.piece_type == PieceType.EMPTY:
                    continue

                scores[piece.piece_color] += piece.value

        return scores[PieceColor.BLACK] - scores[PieceColor.WHITE]

    def get_best_move(self, board: Board):
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf
        best_move = None

        all_maximizer_moves = board.valid_moves[self.color]
        random.shuffle(all_maximizer_moves)

        for move in all_maximizer_moves:
            staged_board = board.apply_move(move)
            score = self.minimax(
                staged_board,
                maximizing_player=False,
                alpha=alpha,
                beta=beta,
                depth=self.depth - 1,
            )
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(
        self,
        board: Board,
        maximizing_player: bool,
        alpha: float,
        beta: float,
        depth: int,
    ):
        current_color = self.color if maximizing_player else PieceColor.WHITE
        score = 0

        if depth == 0:
            score = self.evaluate(board)
            return score

        if not board.valid_moves[current_color]:  # draw or mate
            if board.check_status[current_color]:  # checkmate case
                score = -math.inf if maximizing_player else math.inf
            else:
                score = 0
            return score

        if maximizing_player:
            max_eval = -math.inf
            all_maximizer_moves = board.valid_moves[self.color]

            for move in all_maximizer_moves:
                staged_board = board.apply_move(move)
                staged_eval = self.minimax(
                    staged_board,
                    maximizing_player=False,
                    alpha=alpha,
                    beta=beta,
                    depth=depth - 1,
                )
                max_eval = max(max_eval, staged_eval)

                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break

            return max_eval

        else:
            min_eval = +math.inf
            all_minimizer_moves = board.valid_moves[PieceColor.WHITE]

            for move in all_minimizer_moves:
                staged_board = board.apply_move(move)
                staged_eval = self.minimax(
                    staged_board,
                    maximizing_player=True,
                    alpha=alpha,
                    beta=beta,
                    depth=depth - 1,
                )
                min_eval = min(min_eval, staged_eval)

                beta = min(beta, min_eval)
                if beta <= alpha:
                    break

            return min_eval
