import pygame
import sys
import os
from board.board import Board
import engine
from network.connection import NetworkConnection, DEFAULT_PORT, get_local_ip
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
STATE_ONLINE_MENU = 'online_menu'
STATE_HOST_WAITING = 'host_waiting'
STATE_JOIN_INPUT = 'join_input'
STATE_ONLINE_PLAYING = 'online_playing'

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
        # Online
        self.net = None  # type: ignore
        self.online_role = None  # 'host' or 'client'
        self.ip_input = ""
        self.connection_info = None
        # Create UI elements
        self.create_ui_elements()

    def create_ui_elements(self):
        # Main menu buttons
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 160, 200, 50, "Human vs Human", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 230, 200, 50, "Human with AI", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "Online PvP", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 140, 360, 280, 50, "Random vs Alpha-Beta", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 370, 200, 50, "Continue", WHITE, GREEN),
            Button(SCREEN_WIDTH//2 - 100, 430, 200, 50, "Quit", WHITE, RED)
        ]
        # Difficulty selection buttons (vẽ ở vị trí Random vs Alpha-Beta)
        self.select_difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - 180, 300, 100, 50, "Easy", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 50, 300, 100, 50, "Medium", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 + 80, 300, 100, 50, "Hard", WHITE, GOLD)
        ]
            # Color selection buttons
        self.select_color_buttons = [
                Button(SCREEN_WIDTH//2 - 120, 380, 100, 50, "Red", WHITE, RED),
                Button(SCREEN_WIDTH//2 + 20, 380, 100, 50, "Black", WHITE, BLACK)
            ]

        # Online menu buttons
        self.online_menu_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 230, 200, 50, "Host Game", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "Join Game", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 370, 200, 50, "Back", WHITE, RED)
        ]
        self.join_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 360, 200, 40, "Connect", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 410, 200, 40, "Back", WHITE, RED)
        ]
        self.host_wait_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 410, 200, 40, "Back", WHITE, RED)
        ]
        
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

        if self.state == STATE_ONLINE_MENU:
            font = pygame.font.SysFont('DejaVu Sans Mono', 28, bold=True)
            title2 = font.render("Online PvP", True, BLACK)
            screen.blit(title2, (SCREEN_WIDTH//2 - title2.get_width()//2, 140))
            for b in self.online_menu_buttons:
                b.draw(screen)
        elif self.state == STATE_HOST_WAITING:
            font = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
            ip = self.connection_info or get_local_ip()
            lines = [
                f"Hosting on {ip}:{DEFAULT_PORT}",
                "Waiting for player to join..."
            ]
            for i, t in enumerate(lines):
                surf = font.render(t, True, BLACK)
                screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, 240 + i*40))
            for b in self.host_wait_buttons:
                b.draw(screen)
        elif self.state == STATE_JOIN_INPUT:
            font = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
            label = font.render("Enter Host IP:", True, BLACK)
            screen.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, 220))
            # draw input box
            box_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 260, 300, 40)
            pygame.draw.rect(screen, WHITE, box_rect)
            pygame.draw.rect(screen, BLACK, box_rect, 2)
            text_surf = font.render(self.ip_input or "127.0.0.1", True, BLACK)
            screen.blit(text_surf, (box_rect.x + 8, box_rect.y + 8))
            for b in self.join_buttons:
                b.draw(screen)
        elif self.state == STATE_SELECT_DIFFICULTY:
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
                # Vẽ nút chọn màu quân
                text2 = font.render("Choose your color:", True, BLACK)
                text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, 370))
                screen.blit(text2, text2_rect)
                # Dời các nút chọn màu xuống dưới dòng chữ
                for i, button in enumerate(self.select_color_buttons):
                    button.rect.y = 410
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
        if self.state == STATE_ONLINE_MENU:
            for b in self.online_menu_buttons:
                b.check_hover(pos)
            if click:
                if self.online_menu_buttons[0].is_clicked(pos, click):  # Host
                    self.net = NetworkConnection()
                    ip = self.net.start_host(DEFAULT_PORT)
                    self.connection_info = ip
                    self.online_role = 'host'
                    self.player_color = 'red'
                    self.state = STATE_HOST_WAITING
                elif self.online_menu_buttons[1].is_clicked(pos, click):  # Join
                    self.ip_input = ""
                    self.state = STATE_JOIN_INPUT
                elif self.online_menu_buttons[2].is_clicked(pos, click):  # Back
                    self.state = STATE_MENU
                    return
        elif self.state == STATE_HOST_WAITING:
            for b in self.host_wait_buttons:
                b.check_hover(pos)
            if click and self.host_wait_buttons[0].is_clicked(pos, click):
                if self.net:
                    self.net.close()
                    self.net = None
                self.state = STATE_ONLINE_MENU
            # if a client connects, connected flag will be set in update()
        elif self.state == STATE_JOIN_INPUT:
            for b in self.join_buttons:
                b.check_hover(pos)
            if click:
                if self.join_buttons[0].is_clicked(pos, click):  # Connect
                    host_ip = self.ip_input or "127.0.0.1"
                    self.net = NetworkConnection()
                    ok = self.net.connect(host_ip, DEFAULT_PORT)
                    if ok:
                        self.online_role = 'client'
                        self.player_color = 'black'
                        self.state = STATE_ONLINE_PLAYING
                        self.board = Board()
                    else:
                        # stay and allow retry
                        pass
                elif self.join_buttons[1].is_clicked(pos, click):
                    self.state = STATE_ONLINE_MENU
        elif self.state == STATE_SELECT_DIFFICULTY:
            # Chỉ xử lý nút chọn độ khó
            for i, button in enumerate(self.select_difficulty_buttons):
                button.check_hover(pos)
                if click and button.is_clicked(pos, click):
                    self.ai_difficulty = i + 1
                    self.default_difficulty = i + 1
                    print("AI Difficulty set to:", self.ai_difficulty)
            # Chọn màu quân
            for i, button in enumerate(self.select_color_buttons):
                button.check_hover(pos)
                if click and button.is_clicked(pos, click):
                    if button.text == "Red":
                        self.player_color = 'red'
                        self.state = STATE_PLAYING
                        self.reset_game()
                    elif button.text == "Black":
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
                elif self.menu_buttons[2].is_clicked(pos, click):  # Online PvP
                    self.state = STATE_ONLINE_MENU
                elif self.menu_buttons[3].is_clicked(pos, click):  # Random vs Alpha-Beta
                    self.player_color = 'red'  # không có người chơi
                    self.bot_mode = 'random_vs_alpha'
                    self.state = STATE_PLAYING
                    self.reset_game()
                elif self.menu_buttons[4].is_clicked(pos, click): # Continue
                    if hasattr(self, "paused_board") and self.paused_board is not None:
                        self.board = self.paused_board
                        self.state = STATE_PLAYING
                        self.paused_board = None
                elif self.menu_buttons[5].is_clicked(pos, click): # Quit
                    pygame.quit()
                    sys.exit()
                
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
        # Online hosting: transition when client connects
        if self.state == STATE_HOST_WAITING and self.net:
            if self.net.connected.is_set():
                # Host starts game as red
                self.board = Board()
                self.state = STATE_ONLINE_PLAYING
                return
        # Online playing: poll network messages
        if self.state == STATE_ONLINE_PLAYING and self.net:
            # Process incoming messages
            msg = self.net.get_message()
            if msg:
                if msg.get('type') == 'move':
                    from_pos = tuple(msg['from'])
                    to_pos = tuple(msg['to'])
                    # validate and apply
                    legal = self.board.get_legal_moves(self.board.current_player)
                    if (from_pos, to_pos) in legal:
                        self.board.handle_AI_move(from_pos, to_pos)
                        self.draw_game(); pygame.display.flip()
                elif msg.get('type') == 'disconnect':
                    # back to menu
                    self.state = STATE_MENU
                    if self.net:
                        self.net.close(); self.net = None
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                elif event.type == pygame.KEYDOWN and self.state == STATE_JOIN_INPUT:
                    if event.key == pygame.K_BACKSPACE:
                        self.ip_input = self.ip_input[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # Same as pressing Connect
                        host_ip = self.ip_input or "127.0.0.1"
                        self.net = NetworkConnection()
                        if self.net.connect(host_ip, DEFAULT_PORT):
                            self.online_role = 'client'
                            self.player_color = 'black'
                            self.state = STATE_ONLINE_PLAYING
                            self.board = Board()
                    else:
                        ch = event.unicode
                        if ch and len(ch) == 1 and (ch.isdigit() or ch == '.' or ch == ':'):
                            self.ip_input += ch

            # State machine
            if self.state == STATE_MENU:
                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)
            elif self.state in (STATE_SELECT_DIFFICULTY, STATE_ONLINE_MENU, STATE_HOST_WAITING, STATE_JOIN_INPUT):
                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_PLAYING:
                self.update()
                self.draw_game()
                self.handle_game_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_ONLINE_PLAYING:
                # Only allow moves when it's your turn
                self.update()
                self.draw_game()
                # Send move if player acted
                if mouse_clicked and self.board.current_player == self.player_color:
                    before = len(self.board.move_history)
                    self.handle_game_input(mouse_pos, True)
                    after = len(self.board.move_history)
                    if after > before and self.net:
                        from_pos, to_pos, _, _ = self.board.move_history[-1]
                        self.net.send({'type': 'move', 'from': from_pos, 'to': to_pos})
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