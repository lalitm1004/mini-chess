import sys
import os
import pygame
import math
from typing import Optional, Tuple, Dict, List

from models.board import Board
from models.piece import Piece, PieceColor, PieceType
from models.move import Move
from agent import MinimaxAgent

BOARD_SIZE = 400
SQUARE_SIZE = BOARD_SIZE // 4
PANEL_WIDTH = 250
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH + 40 
WINDOW_HEIGHT = BOARD_SIZE + 80  

COLOR_LIGHT = (238, 238, 210)
COLOR_DARK = (118, 150, 86)
COLOR_BG = (48, 46, 43)
COLOR_PANEL = (38, 36, 33)
COLOR_HIGHLIGHT = (186, 202, 68)
COLOR_VALID_MOVE = (100, 100, 100, 128)
COLOR_CAPTURE_HINT = (200, 50, 50, 128)  
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_GRAY = (150, 150, 150)
COLOR_BUTTON = (60, 60, 60)
COLOR_BUTTON_HOVER = (80, 80, 80)

ASSETS_DIR = os.path.join("assets", "chess_kaneo")
SOUNDS_DIR = os.path.join("assets", "sounds", "sounds")

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, screen, font):
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.action()

class Animation:
    def __init__(self, piece, start_pos, end_pos, duration=15):
        self.piece = piece
        self.start_pos = start_pos 
        self.end_pos = end_pos     
        self.duration = duration   
        self.current_frame = 0
        self.finished = False

    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.duration:
            self.finished = True

    def get_current_pos(self):
        t = self.current_frame / self.duration
        t = 1 - pow(1 - t, 3)
        
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        return (x, y)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        sound_files = {
            "move": "move-self.mp3",
            "capture": "capture.mp3",
            "check": "move-check.mp3",
            "game_start": "game-start.mp3",
            "game_end": "game-end.mp3",
            "notify": "notify.mp3"
        }
        
        for name, filename in sound_files.items():
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Error loading sound {filename}: {e}")
            else:
                print(f"Missing sound asset: {path}")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

class GameApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini-Chess 4x4")
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.SysFont("Arial", 18)
            self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
            self.move_font = pygame.font.SysFont("Monospace", 16)
        except Exception:
            print("Warning: Failed to load system fonts, using default.")
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            self.move_font = pygame.font.Font(None, 20)

        self.images = self.load_assets()
        self.sound_manager = SoundManager()
        self.reset_game()
        
        # UI Elements
        self.reset_btn = Button(
            WINDOW_WIDTH - PANEL_WIDTH + 20, 
            WINDOW_HEIGHT - 60, 
            PANEL_WIDTH - 40, 
            40, 
            "New Game", 
            self.reset_game
        )

    def reset_game(self):
        self.board = Board()
        self.board.compute_game_state()
        self.agent = MinimaxAgent(depth=4)
        
        self.turn = PieceColor.WHITE
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.valid_moves_for_selected: List[Move] = []
        self.last_move: Optional[Move] = None
        self.move_history: List[str] = []
        
        self.game_over = False
        self.winner: Optional[PieceColor] = None
        self.status_message = "White to Move"
        
        self.animation: Optional[Animation] = None
        self.pending_move: Optional[Move] = None
        
        self.sound_manager.play("game_start")

    def load_assets(self) -> Dict[str, pygame.Surface]:
        images = {}
        pieces = {
            (PieceColor.WHITE, PieceType.KING): "wK.svg",
            (PieceColor.WHITE, PieceType.QUEEN): "wQ.svg",
            (PieceColor.WHITE, PieceType.ROOK): "wR.svg",
            (PieceColor.WHITE, PieceType.PAWN): "wP.svg",
            (PieceColor.BLACK, PieceType.KING): "bK.svg",
            (PieceColor.BLACK, PieceType.QUEEN): "bQ.svg",
            (PieceColor.BLACK, PieceType.ROOK): "bR.svg",
            (PieceColor.BLACK, PieceType.PAWN): "bP.svg",
        }
        
        for key, filename in pieces.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
                    images[key] = img
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Missing asset: {path}")
        return images

    def run(self):
        running = True
        while running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            self.reset_btn.handle_event(event)
            
            # Block input during animation
            if self.animation:
                continue
                
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if self.turn == PieceColor.WHITE: # Human turn
                    self.handle_click(event.pos)

    def handle_click(self, pos: Tuple[int, int]):
        board_x = 20
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        
        x, y = pos
        
        # Check if click is inside board
        if board_x <= x < board_x + BOARD_SIZE and board_y <= y < board_y + BOARD_SIZE:
            col = (x - board_x) // SQUARE_SIZE
            row = (y - board_y) // SQUARE_SIZE
            
            clicked_pos = (row, col)
            piece = self.board.grid[row, col]

            # If selecting own piece
            if piece.piece_color == self.turn:
                self.selected_pos = clicked_pos
                self.valid_moves_for_selected = []
                # Filter moves for this piece
                all_valid_moves = self.board.valid_moves[self.turn]
                for move in all_valid_moves:
                    if move.from_pos == clicked_pos:
                        self.valid_moves_for_selected.append(move)
            
            # If moving to a valid square
            elif self.selected_pos:
                move_to_apply = None
                for move in self.valid_moves_for_selected:
                    if move.to_pos == clicked_pos:
                        move_to_apply = move
                        break
                
                if move_to_apply:
                    self.start_move_animation(move_to_apply)
                    self.selected_pos = None
                    self.valid_moves_for_selected = []

    def get_board_pos(self, r, c):
        board_x = 20
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        x = board_x + c * SQUARE_SIZE
        y = board_y + r * SQUARE_SIZE
        return (x, y)

    def start_move_animation(self, move: Move):
        start_pixel = self.get_board_pos(*move.from_pos)
        end_pixel = self.get_board_pos(*move.to_pos)
        
        self.animation = Animation(move.piece, start_pixel, end_pixel)
        self.pending_move = move

    def pos_to_str(self, pos: Tuple[int, int]) -> str:
        r, c = pos
        return f"{chr(ord('a') + c)}{4 - r}"

    def record_move(self, move: Move):
        move_str = f"{self.pos_to_str(move.from_pos)}->{self.pos_to_str(move.to_pos)}"
        
        # If it's White's turn (before switch), it's a new line
        # If it's Black's turn, append to last line
        if self.turn == PieceColor.WHITE:
            turn_num = len(self.move_history) + 1
            self.move_history.append(f"{turn_num}. {move_str}")
        else:
            if self.move_history:
                self.move_history[-1] += f"  {move_str}"

    def finish_move(self):
        if not self.pending_move:
            return
            
        move = self.pending_move
        self.record_move(move)
        
        is_capture = move.captured_piece and move.captured_piece.piece_type != PieceType.EMPTY
        
        self.board = self.board.apply_move(move)
        self.board.compute_game_state()
        self.last_move = move
        self.check_game_over()

        if self.game_over:
            self.sound_manager.play("game_end")
        elif self.board.check_status[PieceColor.WHITE] or self.board.check_status[PieceColor.BLACK]:
            self.sound_manager.play("check")
        elif is_capture:
            self.sound_manager.play("capture")
        else:
            self.sound_manager.play("move")
        
        self.pending_move = None
        self.animation = None
        
        if not self.game_over:
            self.switch_turn()

    def switch_turn(self):
        self.turn = PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE
        if self.turn == PieceColor.WHITE:
            self.status_message = "White to Move"
        else:
            self.status_message = "Black Thinking..."
    
    def update(self):
        if self.animation:
            self.animation.update()
            if self.animation.finished:
                self.finish_move()
            return

        if not self.game_over and self.turn == PieceColor.BLACK:
            pygame.display.flip()
            # Small delay before AI starts thinking to let UI refresh
            pygame.time.wait(50) 
            
            best_move = self.agent.get_best_move(self.board)
            if best_move:
                self.start_move_animation(best_move)
            else:
                pass

    def check_game_over(self):
        white_mate = self.board.checkmate_status[PieceColor.WHITE]
        black_mate = self.board.checkmate_status[PieceColor.BLACK]
        white_stalemate = self.board.stalemate_status[PieceColor.WHITE]
        black_stalemate = self.board.stalemate_status[PieceColor.BLACK]
        
        if white_mate:
            self.game_over = True
            self.winner = PieceColor.BLACK
            self.status_message = "Checkmate! Black Wins!"
        elif black_mate:
            self.game_over = True
            self.winner = PieceColor.WHITE
            self.status_message = "Checkmate! White Wins!"
        elif white_stalemate or black_stalemate:
            self.game_over = True
            self.winner = None
            self.status_message = "Stalemate! Draw!"
        elif self.board.check_status[self.turn]:
             self.status_message = "Check!"

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_board()
        self.draw_panel()
        pygame.display.flip()

    def draw_board(self):
        start_x = 20
        start_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        
        for i in range(4):
            lbl = self.font.render(chr(ord('a') + i), True, COLOR_TEXT_GRAY)
            self.screen.blit(lbl, (start_x + i * SQUARE_SIZE + SQUARE_SIZE - 15, start_y + BOARD_SIZE + 5))
            lbl = self.font.render(str(4 - i), True, COLOR_TEXT_GRAY)
            self.screen.blit(lbl, (start_x - 15, start_y + i * SQUARE_SIZE + 5))

        for row in range(4):
            for col in range(4):
                x = start_x + col * SQUARE_SIZE
                y = start_y + row * SQUARE_SIZE
                
                color = COLOR_LIGHT if (row + col) % 2 == 0 else COLOR_DARK
                
                if self.last_move:
                    if (row, col) == self.last_move.from_pos or (row, col) == self.last_move.to_pos:
                        color = COLOR_HIGHLIGHT
                
                if self.selected_pos == (row, col):
                    color = COLOR_HIGHLIGHT

                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Draw valid move hints
                if self.selected_pos:
                    for move in self.valid_moves_for_selected:
                        if move.to_pos == (row, col):
                            is_capture = move.captured_piece and move.captured_piece.piece_type != PieceType.EMPTY
                            
                            if is_capture:
                                # Draw capture ring
                                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                                pygame.draw.circle(s, COLOR_CAPTURE_HINT, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2, 4)
                                self.screen.blit(s, (x, y))
                            else:
                                # Draw move dot
                                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                                radius = SQUARE_SIZE // 6
                                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                                pygame.draw.circle(s, COLOR_VALID_MOVE, (SQUARE_SIZE//2, SQUARE_SIZE//2), radius)
                                self.screen.blit(s, (x, y))

                # Draw Piece
                # Skip drawing the piece if it is currently animating
                piece = self.board.grid[row, col]
                
                is_animating_source = False
                if self.animation and self.pending_move:
                    if (row, col) == self.pending_move.from_pos:
                        is_animating_source = True
                
                if piece.piece_type != PieceType.EMPTY and not is_animating_source:
                    key = (piece.piece_color, piece.piece_type)
                    if key in self.images:
                        self.screen.blit(self.images[key], (x, y))

        # Draw Animating Piece
        if self.animation:
            key = (self.animation.piece.piece_color, self.animation.piece.piece_type)
            if key in self.images:
                pos = self.animation.get_current_pos()
                self.screen.blit(self.images[key], pos)

    def draw_panel(self):
        panel_x = WINDOW_WIDTH - PANEL_WIDTH
        pygame.draw.rect(self.screen, COLOR_PANEL, (panel_x, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        
        max_width = PANEL_WIDTH - 40
        status_lines = []
        
        status_surf = self.title_font.render(self.status_message, True, COLOR_TEXT)
        
        if status_surf.get_width() > max_width:
            words = self.status_message.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.font.render(test_line, True, COLOR_TEXT)
                
                if test_surf.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        status_lines.append(current_line)
                    current_line = word
            
            if current_line:
                status_lines.append(current_line)
            
            y_offset = 30
            for line in status_lines:
                line_surf = self.font.render(line, True, COLOR_TEXT)
                self.screen.blit(line_surf, (panel_x + 20, y_offset))
                y_offset += 25
        else:
            self.screen.blit(status_surf, (panel_x + 20, 30))
        
        hist_header = self.font.render("Move History", True, COLOR_TEXT_GRAY)
        self.screen.blit(hist_header, (panel_x + 20, 80))
        
        start_y = 110
        moves_to_show = self.move_history[-15:]
        
        for i, move_text in enumerate(moves_to_show): 
            txt = self.move_font.render(move_text, True, COLOR_TEXT)
            self.screen.blit(txt, (panel_x + 20, start_y + i * 25))
            
        self.reset_btn.draw(self.screen, self.font)

if __name__ == "__main__":
    try:
        app = GameApp()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        with open("crash_log.txt", "w") as f:
            traceback.print_exc(file=f)
        pygame.quit()
        sys.exit(1)
