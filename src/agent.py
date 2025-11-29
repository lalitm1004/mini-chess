from __future__ import annotations
from typing import Optional, List
import math

from models.board import Board
from models.piece import PieceColor, PieceType, Piece, SILVERMAN_DEFAULT_START_SCORES
from models.move import Move


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
        presence_scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }

        absence_scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }

        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

        center_scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }

        for r in range(board.size):
            for c in range(board.size):
                piece: Piece = board.grid[r, c]

                if piece.piece_type != PieceType.EMPTY:
                    presence_scores[piece.piece_color] += piece.value
                    if (r, c) in center_positions:
                        center_scores[piece.piece_color] += piece.value

        for color in absence_scores.keys():
            absence_scores[color] = (
                SILVERMAN_DEFAULT_START_SCORES[color] - presence_scores[color]
            )

        # reward for pieces this color threatens
        threatened_reward = {
            PieceColor.WHITE: board.threat_scores[PieceColor.BLACK],
            PieceColor.BLACK: board.threat_scores[PieceColor.WHITE],
        }

        score = (
            presence_scores[PieceColor.BLACK]
            + absence_scores[PieceColor.WHITE]
            + center_scores[PieceColor.BLACK]
            + threatened_reward[PieceColor.BLACK]
        ) - (
            presence_scores[PieceColor.WHITE]
            + absence_scores[PieceColor.BLACK]
            + center_scores[PieceColor.WHITE]
            + threatened_reward[PieceColor.WHITE]
        )
        return score

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
        all_maximizer_moves = self.order_moves(board, all_maximizer_moves)

        for move in all_maximizer_moves:
            staged_board = board.apply_move(move)

            # immediate check for one-move checkmate
            if (
                not staged_board.valid_moves[PieceColor.WHITE]
                and staged_board.check_status[PieceColor.WHITE]
            ):
                score = math.inf
            else:
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
        opponent_color = PieceColor.WHITE if maximizing_player else self.color

        if depth == 0:
            return self.evaluate(board)

        # terminal check: current player
        if not board.valid_moves[current_color]:
            if board.check_status[current_color]:
                return -math.inf if maximizing_player else math.inf
            return 0

        # terminal check: opponent
        if not board.valid_moves[opponent_color]:
            if board.check_status[opponent_color]:
                return math.inf if maximizing_player else -math.inf
            return 0

        if maximizing_player:
            max_eval = -math.inf
            moves = board.valid_moves[self.color]

            for move in moves:
                staged_board = board.apply_move(move)

                # one-move checkmate detection
                if (
                    not staged_board.valid_moves[PieceColor.WHITE]
                    and staged_board.check_status[PieceColor.WHITE]
                ):
                    staged_eval = math.inf
                else:
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
            min_eval = math.inf
            moves = board.valid_moves[PieceColor.WHITE]

            for move in moves:
                staged_board = board.apply_move(move)

                # one-move checkmate detection
                if (
                    not staged_board.valid_moves[self.color]
                    and staged_board.check_status[self.color]
                ):
                    staged_eval = -math.inf
                else:
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

    def order_moves(self, board: Board, moves: List[Move]):
        """Simple move ordering heuristic: prioritize captures.

        Args:
            board (Board): The current board.
            moves (List[Move]): List of legal moves.

        Returns:
            List[Move]: Moves sorted by priority.
        """

        def move_value(move: Move):
            if move.captured_piece:
                return (move.captured_piece.value * 10) - move.piece.value
            return 0

        return sorted(moves, key=move_value, reverse=True)
