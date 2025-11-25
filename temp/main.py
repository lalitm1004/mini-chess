import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import copy


class Piece(Enum):
    EMPTY = 0
    W_KING = 1
    W_QUEEN = 2
    W_ROOK = 3
    W_PAWN = 4
    B_KING = 5
    B_QUEEN = 6
    B_ROOK = 7
    B_PAWN = 8


# Symbol mapping
PIECE_SYMBOLS = {
    Piece.EMPTY: ".",
    Piece.B_KING: "♔",
    Piece.B_QUEEN: "♕",
    Piece.B_ROOK: "♖",
    Piece.B_PAWN: "♙",
    Piece.W_KING: "♚",
    Piece.W_QUEEN: "♛",
    Piece.W_ROOK: "♜",
    Piece.W_PAWN: "♟",
}

# Movement patterns (x, y) - relative moves
PIECE_MOVES = {
    Piece.W_KING: [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ],
    Piece.B_KING: [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ],
    Piece.W_QUEEN: [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]
    + [(i, 0) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(0, i) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(i, i) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(i, -i) for i in range(-3, 4) if i != 0 and abs(i) > 1],
    Piece.B_QUEEN: [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]
    + [(i, 0) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(0, i) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(i, i) for i in range(-3, 4) if i != 0 and abs(i) > 1]
    + [(i, -i) for i in range(-3, 4) if i != 0 and abs(i) > 1],
    Piece.W_ROOK: [(i, 0) for i in range(-3, 4) if i != 0]
    + [(0, i) for i in range(-3, 4) if i != 0],
    Piece.B_ROOK: [(i, 0) for i in range(-3, 4) if i != 0]
    + [(0, i) for i in range(-3, 4) if i != 0],
    Piece.W_PAWN: [(1, 0), (1, -1), (1, 1)],  # Forward and diagonal captures
    Piece.B_PAWN: [(-1, 0), (-1, -1), (-1, 1)],  # Forward (down board) and captures
}

# Piece values
PIECE_VALUES = {
    Piece.EMPTY: 0,
    Piece.W_KING: 1000,
    Piece.W_QUEEN: 9,
    Piece.W_ROOK: 5,
    Piece.W_PAWN: 1,
    Piece.B_KING: 1000,
    Piece.B_QUEEN: 9,
    Piece.B_ROOK: 5,
    Piece.B_PAWN: 1,
}

# Starting positions for 4x4 Silverman
# Row 0: White back rank (Rook, Queen, King, Rook)
# Row 1: White pawns
# Row 2: Black pawns
# Row 3: Black back rank (Rook, King, Queen, Rook)
STARTING_POSITIONS = {
    Piece.W_ROOK: [(0, 0), (0, 3)],
    Piece.W_QUEEN: [(0, 2)],
    Piece.W_KING: [(0, 1)],
    Piece.W_PAWN: [(1, 0), (1, 1), (1, 2), (1, 3)],
    Piece.B_PAWN: [(2, 0), (2, 1), (2, 2), (2, 3)],
    Piece.B_ROOK: [(3, 0), (3, 3)],
    Piece.B_KING: [(3, 1)],
    Piece.B_QUEEN: [(3, 2)],
}


@dataclass
class Move:
    piece: Piece
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    captured_piece: Optional[Piece] = None


class Board:
    def __init__(self, grid=None):
        if grid is None:
            self.grid = np.full((4, 4), Piece.EMPTY, dtype=object)
            for piece, positions in STARTING_POSITIONS.items():
                for pos in positions:
                    self.grid[pos] = piece
        else:
            self.grid = grid

    def get_pieces_in_threat(
        self, is_white: bool
    ) -> Tuple[List[Piece], List[Piece], int, int]:
        """Returns (my_threatened, enemy_threatened, my_threat_value, enemy_threat_value)"""
        my_pieces = []
        enemy_pieces = []

        # Get all pieces and their positions
        for r in range(4):
            for c in range(4):
                piece = self.grid[r, c]
                if piece == Piece.EMPTY:
                    continue

                piece_is_white = piece.value <= 4
                if piece_is_white == is_white:
                    # Check if this piece is under threat
                    if self._is_position_threatened(r, c, not is_white):
                        my_pieces.append(piece)
                else:
                    # Check if this piece is under threat by us
                    if self._is_position_threatened(r, c, is_white):
                        enemy_pieces.append(piece)

        my_value = sum(PIECE_VALUES[p] for p in my_pieces)
        enemy_value = sum(PIECE_VALUES[p] for p in enemy_pieces)

        return my_pieces, enemy_pieces, my_value, enemy_value

    def _is_position_threatened(self, row: int, col: int, by_white: bool) -> bool:
        """Check if a position is threatened by pieces of given color"""
        for r in range(4):
            for c in range(4):
                piece = self.grid[r, c]
                if piece == Piece.EMPTY:
                    continue

                piece_is_white = piece.value <= 4
                if piece_is_white != by_white:
                    continue

                # Check if this piece can attack the target position
                if self._can_attack(r, c, row, col, piece):
                    return True
        return False

    def _can_attack(
        self, from_r: int, from_c: int, to_r: int, to_c: int, piece: Piece
    ) -> bool:
        """Check if a piece can attack a position"""
        moves = PIECE_MOVES.get(piece, [])
        dr, dc = to_r - from_r, to_c - from_c

        # Pawn special case: can only capture diagonally
        if piece in [Piece.W_PAWN, Piece.B_PAWN]:
            return (dr, dc) in moves and dc != 0

        # For rook and queen, check if path is clear
        if piece in [Piece.W_ROOK, Piece.B_ROOK, Piece.W_QUEEN, Piece.B_QUEEN]:
            if (dr, dc) not in moves:
                return False
            return self._is_path_clear(from_r, from_c, to_r, to_c)

        return (dr, dc) in moves

    def _is_path_clear(self, from_r: int, from_c: int, to_r: int, to_c: int) -> bool:
        """Check if path is clear for rook/queen movement"""
        dr = 0 if to_r == from_r else (1 if to_r > from_r else -1)
        dc = 0 if to_c == from_c else (1 if to_c > from_c else -1)

        r, c = from_r + dr, from_c + dc
        while (r, c) != (to_r, to_c):
            if self.grid[r, c] != Piece.EMPTY:
                return False
            r, c = r + dr, c + dc
        return True

    def is_check(self, is_white: bool) -> bool:
        """Check if the given side's king is in check"""
        king = Piece.W_KING if is_white else Piece.B_KING
        king_pos = None

        for r in range(4):
            for c in range(4):
                if self.grid[r, c] == king:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        return self._is_position_threatened(king_pos[0], king_pos[1], not is_white)

    def display(self):
        print("\n  0 1 2 3")
        for i, row in enumerate(self.grid):
            print(f"{i} ", end="")
            for piece in row:
                print(PIECE_SYMBOLS[piece], end=" ")
            print()
        print()


class Bot:
    def __init__(self, is_white: bool, depth: int = 3):
        self.is_white = is_white
        self.depth = depth

    def get_valid_moves(self, board: Board) -> List[Move]:
        """Get all valid moves for bot's pieces"""
        moves = []

        for r in range(4):
            for c in range(4):
                piece = board.grid[r, c]
                if piece == Piece.EMPTY:
                    continue

                piece_is_white = piece.value <= 4
                if piece_is_white != self.is_white:
                    continue

                # Get possible moves for this piece
                piece_moves = PIECE_MOVES.get(piece, [])
                for dr, dc in piece_moves:
                    new_r, new_c = r + dr, c + dc

                    # Check bounds
                    if not (0 <= new_r < 4 and 0 <= new_c < 4):
                        continue

                    target = board.grid[new_r, new_c]

                    # Pawn movement rules
                    if piece in [Piece.W_PAWN, Piece.B_PAWN]:
                        if dc == 0:  # Forward move
                            if target != Piece.EMPTY:
                                continue
                        else:  # Diagonal capture
                            if target == Piece.EMPTY:
                                continue
                            target_is_white = target.value <= 4
                            if target_is_white == piece_is_white:
                                continue
                    else:
                        # Can't capture own pieces
                        if target != Piece.EMPTY:
                            target_is_white = target.value <= 4
                            if target_is_white == piece_is_white:
                                continue

                    # For rooks and queens, check path
                    if piece in [
                        Piece.W_ROOK,
                        Piece.B_ROOK,
                        Piece.W_QUEEN,
                        Piece.B_QUEEN,
                    ]:
                        if not board._is_path_clear(r, c, new_r, new_c):
                            continue

                    move = Move(
                        piece,
                        (r, c),
                        (new_r, new_c),
                        target if target != Piece.EMPTY else None,
                    )

                    # Don't allow moves that leave king in check
                    new_board = self.resolve_state(move, board)
                    if not new_board.is_check(self.is_white):
                        moves.append(move)

        return moves

    def resolve_state(self, move: Move, board: Board) -> Board:
        """Return new board state after applying move"""
        new_grid = board.grid.copy()
        new_grid[move.from_pos] = Piece.EMPTY
        new_grid[move.to_pos] = move.piece
        return Board(new_grid)

    def evaluate_board(self, board: Board) -> float:
        """Heuristic evaluation function"""
        score = 0

        # Material count
        for r in range(4):
            for c in range(4):
                piece = board.grid[r, c]
                if piece == Piece.EMPTY:
                    continue

                value = PIECE_VALUES[piece]
                piece_is_white = piece.value <= 4

                if piece_is_white == self.is_white:
                    score += value
                else:
                    score -= value

        # Check/checkmate bonus
        if board.is_check(not self.is_white):
            score += 50
        if board.is_check(self.is_white):
            score -= 50

        # Threatened pieces
        _, enemy_threat, _, enemy_threat_val = board.get_pieces_in_threat(self.is_white)
        my_threat, _, my_threat_val, _ = board.get_pieces_in_threat(not self.is_white)

        score += enemy_threat_val * 0.1
        score -= my_threat_val * 0.1

        return score

    def minimax(
        self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool
    ) -> Tuple[float, Optional[Move]]:
        """Minimax with alpha-beta pruning"""
        if depth == 0:
            return self.evaluate_board(board), None

        moves = (
            self.get_valid_moves(board)
            if maximizing
            else Bot(not self.is_white).get_valid_moves(board)
        )

        if not moves:
            # No valid moves - check if checkmate or stalemate
            is_check = board.is_check(
                self.is_white if maximizing else not self.is_white
            )
            if is_check:
                return -10000 if maximizing else 10000, None
            return 0, None  # Stalemate

        best_move = None

        if maximizing:
            max_eval = float("-inf")
            for move in moves:
                new_board = self.resolve_state(move, board)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float("inf")
            opponent_bot = Bot(not self.is_white)
            for move in moves:
                new_board = opponent_bot.resolve_state(move, board)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def make_move(self, board: Board) -> Move:
        """Find and return best move"""
        _, best_move = self.minimax(
            board, self.depth, float("-inf"), float("inf"), True
        )
        return best_move


def turn_human(board: Board, is_white: bool) -> Board:
    """Human player turn"""
    while True:
        try:
            print(f"{'White' if is_white else 'Black'} to move")
            from_input = input("From (row col): ").strip().split()
            to_input = input("To (row col): ").strip().split()

            from_r, from_c = int(from_input[0]), int(from_input[1])
            to_r, to_c = int(to_input[0]), int(to_input[1])

            piece = board.grid[from_r, from_c]
            if piece == Piece.EMPTY:
                print("No piece at that position!")
                continue

            piece_is_white = piece.value <= 4
            if piece_is_white != is_white:
                print("That's not your piece!")
                continue

            move = Move(piece, (from_r, from_c), (to_r, to_c), board.grid[to_r, to_c])

            # Validate move
            bot = Bot(is_white)
            valid_moves = bot.get_valid_moves(board)

            if any(
                m.from_pos == move.from_pos and m.to_pos == move.to_pos
                for m in valid_moves
            ):
                return bot.resolve_state(move, board)
            else:
                print("Invalid move!")
        except (ValueError, IndexError):
            print("Invalid input format!")


def turn_bot(bot: Bot, board: Board) -> Board:
    """Bot player turn"""
    print(f"{'White' if bot.is_white else 'Black'} (Bot) thinking...")
    move = bot.make_move(board)
    if move:
        print(
            f"Bot moves {PIECE_SYMBOLS[move.piece]} from {move.from_pos} to {move.to_pos}"
        )
        return bot.resolve_state(move, board)
    return board


# Main game loop
def play_game():
    board = Board()
    bot = Bot(is_white=False, depth=3)  # Bot plays black

    board.display()

    while True:
        # Human (white) turn
        board = turn_human(board, True)
        board.display()

        if board.is_check(False):
            print("Black is in check!")

        # Check for game over
        bot_moves = bot.get_valid_moves(board)
        if not bot_moves:
            if board.is_check(False):
                print("Checkmate! White wins!")
            else:
                print("Stalemate!")
            break

        # Bot (black) turn
        board = turn_bot(bot, board)
        board.display()

        if board.is_check(True):
            print("White is in check!")

        # Check for game over
        white_bot = Bot(is_white=True)
        white_moves = white_bot.get_valid_moves(board)
        if not white_moves:
            if board.is_check(True):
                print("Checkmate! Black wins!")
            else:
                print("Stalemate!")
            break


if __name__ == "__main__":
    play_game()
