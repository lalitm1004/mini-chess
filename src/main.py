import sys
from typing import Optional, Tuple

from agent import MinimaxAgent
from models.board import Board
from models.piece import PieceColor


def print_board(board: Board):
    print("  a b c d")
    print(" +-------+")
    for r in range(board.size):
        row_str = f"{board.size - r}|"
        for c in range(board.size):
            piece = board.grid[r, c]
            row_str += f"{piece.symbol} "
        print(row_str.strip() + "|")
    print(" +-------+")


def parse_position(pos_str: str) -> Optional[Tuple[int, int]]:
    if len(pos_str) != 2:
        return None

    col_char = pos_str[0].lower()
    row_char = pos_str[1]

    if col_char not in ["a", "b", "c", "d"]:
        return None

    try:
        row_num = int(row_char)
    except ValueError:
        return None

    if not (1 <= row_num <= 4):
        return None

    # 0-idx (row 0 is top, row 3 is bottom)
    r = 4 - row_num
    c = ord(col_char) - ord("a")

    return (r, c)


def main():
    print("You are White (Bottom, UpperCase). Agent is Black (Top, LowerCase)")
    print("Enter moves as 'a2 a3'")

    board = Board()
    agent = MinimaxAgent()

    turn = PieceColor.WHITE

    while True:
        print_board(board)

        # check for game over
        if not board.valid_moves[turn]:
            if board.check_status[turn]:
                winner = "Black" if turn == PieceColor.WHITE else "White"
                print(f"Checkmate! {winner} wins!")
            else:
                print("Stalemate!")
            break

        if turn == PieceColor.WHITE:
            # user turn
            while True:
                try:
                    move_str = input("Enter move: ").strip()
                    if move_str.lower() in ["quit", "exit"]:
                        sys.exit(0)

                    parts = move_str.split()
                    if len(parts) != 2:
                        print("Invalid format. Use 'a2 a3'.")
                        continue

                    from_pos = parse_position(parts[0])
                    to_pos = parse_position(parts[1])

                    if not from_pos or not to_pos:
                        print("Invalid coordinates.")
                        continue

                    valid_moves = board.valid_moves[PieceColor.WHITE]
                    selected_move = None

                    for move in valid_moves:
                        if move.from_pos == from_pos and move.to_pos == to_pos:
                            selected_move = move
                            break

                    if not selected_move:
                        print("Invalid move.")
                        continue

                    next_board = board.apply_move(selected_move)
                    if next_board.check_status[PieceColor.WHITE]:
                        print("Illegal move: King would be in check!")
                        continue

                    board = next_board
                    break

                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")
                    continue

            turn = PieceColor.BLACK

        else:
            # agent turn
            print("Agent is thinking...")
            best_move = agent.get_best_move(board)

            if best_move:
                # convert back to string for display
                r_from, c_from = best_move.from_pos
                r_to, c_to = best_move.to_pos

                from_str = f"{chr(ord('a') + c_from)}{4 - r_from}"
                to_str = f"{chr(ord('a') + c_to)}{4 - r_to}"

                print(f"Agent plays: {from_str} {to_str}")
                board = board.apply_move(best_move)
            else:
                print("Agent has no moves (should be handled by game over check).")

            turn = PieceColor.WHITE


if __name__ == "__main__":
    main()
