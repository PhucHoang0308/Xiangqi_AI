import pygame
import sys
import os
from board.board import Board
import engine
from search.random_bot import random_bot_move
import time
# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 550, 680
FPS = 60
WINDOW_TITLE = "Zhongguo Xiangqi"

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Game status
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_GAME_OVER = 'game_over'
STATE_PAUSED = 'paused'
STATE_SELECT_DIFFICULTY = 'select_difficulty'
STATE_ONLINE_SETUP = 'online_setup'

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

class Button:
    """Simple button class for UI"""
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered    

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Game:
    """Main game class"""
    def __init__(self):
        self.state = STATE_MENU
        self.board = None
        self.engine = None
        self.player_color = 'red'
        self.ai_difficulty = 2
        self.clock = pygame.time.Clock()
        self.winner = None
        self.bot_mode = None  # 'random_vs_alpha' hoặc None
        self.default_difficulty = 2
        self.network = None
        self.is_online = False
        # Difficulty selection buttons (vẽ ở vị trí Random vs Alpha-Beta)
        self.select_difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - 180, 300, 100, 50, "Easy", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 50, 300, 100, 50, "Medium", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 + 80, 300, 100, 50, "Hard", WHITE, GOLD)
        ]
        # Online setup variables
        self.online_ip = "127.0.0.1"
        self.online_port = 5000
        self.online_mode = None  # 'host' or 'client'
        self.online_buttons = [
            Button(SCREEN_WIDTH//2 - 120, 220, 100, 40, "Host", WHITE, BLUE),
            Button(SCREEN_WIDTH//2 + 20, 220, 100, 40, "Client", WHITE, BLUE),
            Button(SCREEN_WIDTH//2 - 100, 320, 200, 50, "Kết nối", WHITE, GREEN)
        ]
        # Create UI elements
        self.create_ui_elements()

    def create_ui_elements(self):
        # Main menu buttons
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 160, 200, 50, "Human vs Human", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 230, 200, 50, "Human with AI", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 140, 300, 280, 50, "Random vs Alpha-Beta", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 370, 200, 50, "Play Online (PvsP)", WHITE, BLUE),
            Button(SCREEN_WIDTH//2 - 100, 430, 200, 50, "Continue", WHITE, GREEN),
            Button(SCREEN_WIDTH//2 - 100, 490, 200, 50, "Quit", WHITE, RED)
        ]
    # ...existing code...
        
        # Difficulty buttons
        self.difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - 180, 480, 100, 40, "Easy", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 50, 480, 100, 40, "Medium", WHITE, GOLD),  # Default selected
            Button(SCREEN_WIDTH//2 + 80, 480, 100, 40, "Hard", WHITE, GOLD)
        ]

        # In-game buttons
        self.game_buttons = [
            Button(10, 10, 80, 30, "Menu", WHITE, GOLD),
            Button(100, 10, 80, 30, "Quit", WHITE, RED),
        ]

        # Game over buttons
        self.game_over_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "Play Again", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 370, 200, 50, "Main Menu", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 440, 200, 50, "Quit", WHITE, RED)
        ]

    def reset_game(self):
        """Reset the game state to startr a new game"""
        self.board = Board()
        
        # TODO If player is Black, AI(red) goes first
        # if self.player_color == 'black' and self.state == STATE_PLAYING:
        #     self.ai_make_move()

    def draw_menu(self):
        """Draw the main menu screen"""
        screen.fill(WHITE)
        self.bot_mode = None
        # Draw title
        font = pygame.font.SysFont('DejaVu Sans Mono', 44, bold=True)
        title = font.render("Zhongguo Xiangqi", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 70))
        screen.blit(title, title_rect)

        if self.state == STATE_SELECT_DIFFICULTY:
            # Chỉ vẽ nút chọn độ khó ở vị trí Random vs Alpha-Beta
            font = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
            text = font.render("AI Difficulty:", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 250))
            screen.blit(text, text_rect)
            for i, button in enumerate(self.select_difficulty_buttons):
                if i + 1 == self.ai_difficulty:
                    button.color = GREEN
                else:
                    button.color = WHITE
                button.draw(screen)
        else:
            # Vẽ các nút menu bình thường
            for i, button in enumerate(self.menu_buttons):
                if button.text == "Continue":
                    if not hasattr(self, "paused_board") or self.paused_board is None:
                        continue
                button.draw(screen)

    def draw_game(self):
        """Draw the game screen with board and pieces"""
        # Let the board draw itself
        self.board.draw(screen)

        # Draw game buttons
        for button in self.game_buttons:
            button.draw(screen)

        # Draw current player indicator
        font = pygame.font.SysFont('DejaVu Sans Mono', 20, bold=True)
        player_text = f"Current Player: {'Red' if self.board.current_player == 'red' else 'Black'}"
        text_surface = font.render(player_text, True, RED if self.board.current_player == 'red' else BLACK)
        screen.blit(text_surface, (290, 15))

        # TODO Draw thingking indicator if AI is calculating
        if self.bot_mode == 'random_vs_alpha':
            ai_info = font.render("Random Bot vs Alpha-Beta", True, BLUE)
            screen.blit(ai_info, (SCREEN_WIDTH//2 - ai_info.get_width()//2, 65))

        # Check for checkmate/game over
        if self.board.is_checkmate('red'):
            self.winner = 'Black'
            self.state = STATE_GAME_OVER
        elif self.board.is_checkmate('black'):
            self.winner = 'Red'
            self.state = STATE_GAME_OVER
        elif self.board.is_game_over():  # Thêm kiểm tra hòa cờ
            self.winner = None
            self.state = STATE_GAME_OVER

        # Check for check(chieu tuong)
        if self.board.is_in_check('red') or self.board.is_in_check('black'):
            check_color = 'red' if self.board.is_in_check('red') else 'black'
            check_text = font.render(f"{check_color.capitalize()} is in check!", True, BLUE)
            screen.blit(check_text, (SCREEN_WIDTH//2 - check_text.get_width()//2, 45))

    def draw_game_over(self):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw game over message
        font = pygame.font.SysFont('DejaVu Sans Mono', 44, bold=True)
        message = f"{'Red' if self.winner == 'Red' else 'Black'} Wins!"
        text_color = RED if self.winner == 'Red' else BLACK
        text_surface = font.render(message, True, text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(text_surface, text_rect)

        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(screen)

    def handle_menu_input(self, pos, click):
        """Handle input on the menu screen"""
        if self.state == STATE_SELECT_DIFFICULTY:
            # Chỉ xử lý nút chọn độ khó
            for i, button in enumerate(self.select_difficulty_buttons):
                button.check_hover(pos)
                if click and button.is_clicked(pos, click):
                    self.ai_difficulty = i + 1
                    self.default_difficulty = i + 1
                    print("AI Difficulty set to:", self.ai_difficulty)
                    self.player_color = 'black'
                    self.state = STATE_PLAYING
                    self.reset_game()
        else:
            # Update button hover states
            for button in self.menu_buttons:
                button.check_hover(pos)
            if click:
                if self.menu_buttons[0].is_clicked(pos, click): # Human vs Human
                    self.player_color = None
                    self.state = STATE_PLAYING
                    self.reset_game()
                elif self.menu_buttons[1].is_clicked(pos, click): # Play with AI
                    self.state = STATE_SELECT_DIFFICULTY
                elif self.menu_buttons[2].is_clicked(pos, click):  # Random vs Alpha-Beta
                    self.player_color = 'red'  # không có người chơi
                    self.bot_mode = 'random_vs_alpha'
                    self.state = STATE_PLAYING
                    self.reset_game()
                elif self.menu_buttons[3].is_clicked(pos, click): # Play Online (PvsP)
                    self.state = STATE_ONLINE_SETUP
                elif self.menu_buttons[4].is_clicked(pos, click): # Continue
                    if hasattr(self, "paused_board") and self.paused_board is not None:
                        self.board = self.paused_board
                        self.state = STATE_PLAYING
                        self.paused_board = None
                elif self.menu_buttons[5].is_clicked(pos, click): # Quit
                    pygame.quit()
                    sys.exit()
    def draw_online_setup(self):
        screen.fill(WHITE)
        font = pygame.font.SysFont('DejaVu Sans Mono', 44, bold=True)
        title = font.render("Online Setup", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 70))
        screen.blit(title, title_rect)
        # Draw Host/Client buttons
        for button in self.online_buttons[:2]:
            button.draw(screen)
        # Draw IP/Port input (hiển thị giá trị hiện tại)
        font2 = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
        ip_text = font2.render(f"IP: {self.online_ip}", True, BLACK)
        port_text = font2.render(f"Port: {self.online_port}", True, BLACK)
        screen.blit(ip_text, (SCREEN_WIDTH//2 - 100, 270))
        screen.blit(port_text, (SCREEN_WIDTH//2 - 100, 300))
        # Draw Connect button
        self.online_buttons[2].draw(screen)
        # Hướng dẫn nhập IP/Port bằng phím (có thể nâng cấp ô nhập text sau)
        hint = font2.render("Nhấn I để nhập IP, P để nhập Port", True, BLUE)
        screen.blit(hint, (SCREEN_WIDTH//2 - 150, 360))
    def handle_online_setup_input(self, pos, click, events):
        for button in self.online_buttons[:2]:
            button.check_hover(pos)
        self.online_buttons[2].check_hover(pos)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    # Nhập IP qua terminal
                    ip = input("Nhập IP host (mặc định 127.0.0.1): ").strip() or "127.0.0.1"
                    self.online_ip = ip
                elif event.key == pygame.K_p:
                    port = input("Nhập port (mặc định 5000): ").strip()
                    self.online_port = int(port) if port else 5000
        if click:
            if self.online_buttons[0].is_clicked(pos, click):
                self.online_mode = 'host'
            elif self.online_buttons[1].is_clicked(pos, click):
                self.online_mode = 'client'
            elif self.online_buttons[2].is_clicked(pos, click):
                if self.online_mode:
                    from network import XiangqiNetwork
                    is_host = (self.online_mode == 'host')
                    self.network = XiangqiNetwork(is_host, self.online_ip, self.online_port)
                    self.network.start()
                    self.is_online = True
                    self.player_color = 'red' if is_host else 'black'
                    self.state = STATE_PLAYING
                    self.reset_game()
                
    def handle_game_input(self, pos, click):
        """Handle input on the game screen"""
        # Update button hover states
        for button in self.game_buttons:
            button.check_hover(pos)
        # Handle button clicks
        if click:
            if self.game_buttons[0].is_clicked(pos, click): # Menu
                # Lưu trạng thái bàn cờ khi tạm dừng
                self.paused_board = self.board
                self.state = STATE_MENU
                return
            elif self.game_buttons[1].is_clicked(pos, click): # Quit
                pygame.quit()
                sys.exit()
            # Handle board clicks (if it's player's turn)
            if (self.board.current_player == self.player_color or self.player_color is None):
                self.board.handle_click(pos)
    
    def handle_game_over_input(self, pos, click):
        """Handle input on the game over screen"""
        for button in self.game_over_buttons:
            button.check_hover(pos)
            if click and button.is_clicked(pos, click):
                if button.text == "Play Again":
                    self.reset_game()
                    self.state = STATE_PLAYING
                elif button.text == "Main Menu":
                    self.state = STATE_MENU
                elif button.text == "Quit":
                    pygame.quit()
                    sys.exit()
        
    # TODO: Make AI move

    def update(self):
        """Update game state"""
        # Check if the game is over
        if self.board and self.board.is_game_over():
            if self.board.is_checkmate('red'):
                self.winner = 'Black'
                self.state = STATE_GAME_OVER 
            elif self.board.is_checkmate('black'):
                self.winner = 'Red'
                self.state = STATE_GAME_OVER
            return 
        if self.bot_mode == 'random_vs_alpha':
            if self.board.current_player == 'black':
                random_bot_move(self.board)
                self.draw_game()
                pygame.display.flip()
            else:
                engine.engine(self.board, 'red', type='alpha_beta', difficulty=self.ai_difficulty)
                self.draw_game()
                pygame.display.flip()
                if self.board.is_repeating_state('red'):
                    self.ai_difficulty += 1
                    print(f"⚡ Phát hiện lặp, tăng depth = {self.ai_difficulty} để tính lại...")
                else:
                    self.ai_difficulty = self.default_difficulty
            return
        if self.player_color:
            # AI's turn to think
            if self.board.current_player != self.player_color:
                # Vẽ lại trước khi AI đi
                self.draw_game()
                pygame.display.flip()
                engine.engine(self.board, self.board.current_player, type='alpha_beta', difficulty=self.ai_difficulty)
                # Vẽ lại sau khi AI đi
                self.draw_game()
                pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True

            # State machine
            if self.state == STATE_MENU:
                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_SELECT_DIFFICULTY:
                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_ONLINE_SETUP:
                self.draw_online_setup()
                self.handle_online_setup_input(mouse_pos, mouse_clicked, events)
            elif self.state == STATE_PLAYING:
                self.update()
                self.draw_game()
                self.handle_game_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_GAME_OVER:
                self.draw_game()
                self.draw_game_over()
                self.handle_game_over_input(mouse_pos, mouse_clicked)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
    def run_experiment_random_vs_ai(self):
        """Chạy thử nghiệm Random Bot vs AI Bot với 3 độ khó, 10 ván mỗi độ khó."""
        results = {
            1: {"win": 0, "loss": 0, "draw": 0},
            2: {"win": 0, "loss": 0, "draw": 0},
            3: {"win": 0, "loss": 0, "draw": 0},
        }

        for difficulty in [1, 2, 3]:
            print(f"\n=== Đang chạy 10 trận với độ khó {difficulty} (Easy/Medium/Hard) ===")
            for game_idx in range(10):
                start_time = time.time()
                total_moves = 0
                self.board = Board()
                self.ai_difficulty = difficulty
                self.default_difficulty = difficulty
                self.bot_mode = 'random_vs_alpha'  # Random bot vs AlphaBeta AI
                default_repeat=3
                while not self.board.is_game_over():
                    total_moves += 1
                    if self.board.current_player == 'black':
                        random_bot_move(self.board)
                    else:
                        engine.engine(self.board, 'red', type='alpha_beta', difficulty=self.ai_difficulty)
                        
                        if self.board.is_repeating_state('red', default_repeat):
                            self.ai_difficulty += 1
                            default_repeat +=3
                            print(f"⚡ Phát hiện lặp, tăng depth = {self.ai_difficulty} để tính lại...")
                        else:
                            default_repeat = 3
                            self.ai_difficulty = self.default_difficulty
                time_taken = time.time() - start_time
                # Xử lý kết quả
                if self.board.is_checkmate('red'):
                    results[difficulty]["loss"] += 1  # Random thắng
                elif self.board.is_checkmate('black'):
                    results[difficulty]["win"] += 1   # AI thắng
                else:
                    results[difficulty]["draw"] += 1  # Hòa

                print(f"  - Trận {game_idx + 1}/10 hoàn thành.")
                print(f"  - Thời gian trận {game_idx + 1}: {time_taken:.2f} giây, tổng số nước đi: {total_moves}.")
                print(f"  - Trận {game_idx + 1}/10: AI thắng {results[difficulty]['win']}, Random thắng {results[difficulty]['loss']}, Hòa {results[difficulty]['draw']}")

        # In tổng kết
        print("\n=== Tổng kết ===")
        for difficulty in [1, 2, 3]:
            print(f"Độ khó {difficulty}: AI thắng {results[difficulty]['win']} trận, Random thắng {results[difficulty]['loss']} trận, Hòa {results[difficulty]['draw']} trận.")


           
# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()