from __future__ import annotations
from typing import Optional
import math
import random

from models.board import Board
from models.move import Move
from models.piece import PieceColor, PieceType, Piece


class MinimaxAgent:
    """A simple minimax chess agent with alpha-beta pruning.

    Attributes:
        depth (int): Maximum recursion depth for the minimax search.
        color (PieceColor): The agent's assigned color (defaults to BLACK).
    """

    def __init__(self, depth: int = 100) -> None:
        """Initialize a MinimaxAgent.

        Args:
            depth (int, optional): Depth of minimax search. Defaults to 4.
        """
        self.depth: int = depth
        self.color: PieceColor = PieceColor.BLACK

    def evaluate(self, board: Board) -> int:
        """Evaluate the current board position from the AI's perspective.

        Args:
            board (Board): The game board to evaluate.

        Returns:
            int: A heuristic scoring of the board state. Positive means BLACK advantage,
                negative means WHITE advantage.
        """
        scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }

        for r in range(board.size):
            for c in range(board.size):
                piece: Piece = board.grid[r, c]
                if piece.piece_type != PieceType.EMPTY:
                    scores[piece.piece_color] += piece.value

        return scores[PieceColor.BLACK] - scores[PieceColor.WHITE]

    def get_best_move(self, board: Board) -> Optional[Move]:
        """Get the best move for the current player using minimax search.

        Args:
            board (Board): The current game board.

        Returns:
            Optional[Move]: The best move found, or None if no legal moves exist.
        """
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf
        best_move: Optional[Move] = None

        all_maximizer_moves = board.valid_moves[self.color]
        random.shuffle(all_maximizer_moves)  # chaos improves unpredictability

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
    ) -> float:
        """Recursive minimax search with alpha-beta pruning.

        Args:
            board (Board): The current game state.
            maximizing_player (bool): Whether the current layer is maximizing.
            alpha (float): Current alpha (best already explored for maximizer).
            beta (float): Current beta (best already explored for minimizer).
            depth (int): Remaining search depth.

        Returns:
            float: The heuristic score of the evaluated board.
        """
        current_color = self.color if maximizing_player else PieceColor.WHITE

        # depth reached
        if depth == 0:
            return self.evaluate(board)

        if not board.valid_moves[current_color]:
            if board.check_status[current_color]:  # checkmate
                return -math.inf if maximizing_player else math.inf
            return 0  # stalemate

        # maximizer branch
        if maximizing_player:
            max_eval = -math.inf
            moves = board.valid_moves[self.color]

            for move in moves:
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
                    break  # pruning

            return max_eval

        # minimizer branch
        min_eval = math.inf
        moves = board.valid_moves[PieceColor.WHITE]

        for move in moves:
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
                break  # more pruning

        return min_eval
