import pygame
import sys
import os
from board.board import Board
import engine
from network.connection import NetworkConnection, DEFAULT_PORT, get_local_ip
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
GRAY = (128, 128, 128)

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
        self.default_difficulty = 2
        # Online
        self.net = None  # type: ignore
        self.online_role = None  # 'host' or 'client'
        self.ip_input = ""
        self.connection_info = None
        self.connection_error = None
        self.opponent_disconnected = False
        # Create UI elements
        self.create_ui_elements()

    def create_ui_elements(self):
        # Main menu buttons
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 100, 160, 200, 50, "Human vs Human", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 230, 200, 50, "Human with AI", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 300, 200, 50, "Online PvP", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 100, 370, 200, 50, "Continue", WHITE, GREEN),
            Button(SCREEN_WIDTH//2 - 100, 440, 200, 50, "Quit", WHITE, RED)
        ]
        # Difficulty selection buttons
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
            Button(SCREEN_WIDTH//2 - 100, 410, 200, 40, "Cancel", WHITE, RED)
        ]
        
        # Difficulty buttons
        self.difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - 180, 480, 100, 40, "Easy", WHITE, GOLD),
            Button(SCREEN_WIDTH//2 - 50, 480, 100, 40, "Medium", WHITE, GOLD),
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
        """Reset the game state to start a new game"""
        self.board = Board()
        self.opponent_disconnected = False

    def draw_menu(self):
        """Draw the main menu screen"""
        screen.fill(WHITE)
        
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
            font = pygame.font.SysFont('DejaVu Sans Mono', 20, bold=True)
            ip = self.connection_info or get_local_ip()
            lines = [
                "Waiting for opponent...",
                "",
                f"Your IP: {ip}",
                f"Port: {DEFAULT_PORT}",
                "",
                "Share this IP with your friend!"
            ]
            y_start = 200
            for i, t in enumerate(lines):
                color = BLUE if "IP:" in t or "Port:" in t else BLACK
                surf = font.render(t, True, color)
                screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, y_start + i*30))
            for b in self.host_wait_buttons:
                b.draw(screen)
        elif self.state == STATE_JOIN_INPUT:
            font = pygame.font.SysFont('DejaVu Sans Mono', 22, bold=True)
            label = font.render("Enter Host IP:", True, BLACK)
            screen.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, 200))
            
            # draw input box
            box_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 240, 300, 40)
            pygame.draw.rect(screen, WHITE, box_rect)
            pygame.draw.rect(screen, BLACK, box_rect, 2)
            text_surf = font.render(self.ip_input or "192.168.1.x", True, GRAY if not self.ip_input else BLACK)
            screen.blit(text_surf, (box_rect.x + 8, box_rect.y + 8))
            
            # Show error if connection failed
            if self.connection_error:
                error_font = pygame.font.SysFont('DejaVu Sans Mono', 18, bold=True)
                error_surf = error_font.render(self.connection_error, True, RED)
                screen.blit(error_surf, (SCREEN_WIDTH//2 - error_surf.get_width()//2, 300))
            
            for b in self.join_buttons:
                b.draw(screen)
        elif self.state == STATE_SELECT_DIFFICULTY:
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
            # Draw color selection
            text2 = font.render("Choose your color:", True, BLACK)
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, 370))
            screen.blit(text2, text2_rect)
            for i, button in enumerate(self.select_color_buttons):
                button.rect.y = 410
                button.draw(screen)
        else:
            # Draw normal menu buttons
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

        # Show online game info
        if self.state == STATE_ONLINE_PLAYING:
            info_font = pygame.font.SysFont('DejaVu Sans Mono', 16, bold=True)
            your_color = f"You: {'Red' if self.player_color == 'red' else 'Black'}"
            color_surface = info_font.render(your_color, True, RED if self.player_color == 'red' else BLACK)
            screen.blit(color_surface, (10, 50))
            
            # Show turn indicator
            if self.board.current_player == self.player_color:
                turn_text = "Your Turn"
                turn_color = GREEN
            else:
                turn_text = "Opponent's Turn"
                turn_color = BLUE
            turn_surface = info_font.render(turn_text, True, turn_color)
            screen.blit(turn_surface, (SCREEN_WIDTH - turn_surface.get_width() - 10, 50))
            
            # Show opponent disconnected warning
            if self.opponent_disconnected:
                warning_font = pygame.font.SysFont('DejaVu Sans Mono', 18, bold=True)
                warning_text = warning_font.render("Opponent Disconnected!", True, RED)
                screen.blit(warning_text, (SCREEN_WIDTH//2 - warning_text.get_width()//2, 75))

        # Check for checkmate/game over
        if self.board.is_checkmate('red'):
            self.winner = 'Black'
            self.state = STATE_GAME_OVER
        elif self.board.is_checkmate('black'):
            self.winner = 'Red'
            self.state = STATE_GAME_OVER
        elif self.board.is_game_over():
            self.winner = None
            self.state = STATE_GAME_OVER

        # Check for check
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
        if self.winner:
            message = f"{'Red' if self.winner == 'Red' else 'Black'} Wins!"
            text_color = RED if self.winner == 'Red' else BLACK
        else:
            message = "Draw!"
            text_color = BLUE
        text_surface = font.render(message, True, text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(text_surface, text_rect)

        # Draw buttons (hide Play Again in online mode)
        for button in self.game_over_buttons:
            if button.text == "Play Again" and self.state == STATE_GAME_OVER and self.net:
                continue  # Skip Play Again button in online games
            button.draw(screen)

    def handle_menu_input(self, pos, click):
        """Handle input on the menu screen"""
        if self.state == STATE_ONLINE_MENU:
            for b in self.online_menu_buttons:
                b.check_hover(pos)
            if click:
                if self.online_menu_buttons[0].is_clicked(pos, click):  # Host
                    try:
                        self.net = NetworkConnection()
                        ip = self.net.start_host(DEFAULT_PORT)
                        self.connection_info = ip
                        self.online_role = 'host'
                        self.player_color = 'red'
                        self.state = STATE_HOST_WAITING
                        self.connection_error = None
                    except Exception as e:
                        self.connection_error = f"Failed to host: {str(e)}"
                        if self.net:
                            self.net.close()
                            self.net = None
                elif self.online_menu_buttons[1].is_clicked(pos, click):  # Join
                    self.ip_input = ""
                    self.connection_error = None
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
        elif self.state == STATE_JOIN_INPUT:
            for b in self.join_buttons:
                b.check_hover(pos)
            if click:
                if self.join_buttons[0].is_clicked(pos, click):  # Connect
                    host_ip = self.ip_input.strip()
                    if not host_ip:
                        self.connection_error = "Please enter an IP address"
                        return
                    
                    try:
                        self.net = NetworkConnection()
                        ok = self.net.connect(host_ip, DEFAULT_PORT)
                        if ok:
                            self.online_role = 'client'
                            self.player_color = 'black'
                            self.state = STATE_ONLINE_PLAYING
                            self.board = Board()
                            self.connection_error = None
                        else:
                            self.connection_error = "Connection failed. Check IP and try again."
                            self.net.close()
                            self.net = None
                    except Exception as e:
                        self.connection_error = f"Error: {str(e)}"
                        if self.net:
                            self.net.close()
                            self.net = None
                elif self.join_buttons[1].is_clicked(pos, click):
                    self.state = STATE_ONLINE_MENU
                    self.connection_error = None
        elif self.state == STATE_SELECT_DIFFICULTY:
            # Handle difficulty selection
            for i, button in enumerate(self.select_difficulty_buttons):
                button.check_hover(pos)
                if click and button.is_clicked(pos, click):
                    self.ai_difficulty = i + 1
                    self.default_difficulty = i + 1
                    print("AI Difficulty set to:", self.ai_difficulty)
            # Handle color selection
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
                if self.menu_buttons[0].is_clicked(pos, click):  # Human vs Human
                    self.player_color = None
                    self.state = STATE_PLAYING
                    self.reset_game()
                elif self.menu_buttons[1].is_clicked(pos, click):  # Play with AI
                    self.state = STATE_SELECT_DIFFICULTY
                elif self.menu_buttons[2].is_clicked(pos, click):  # Online PvP
                    self.state = STATE_ONLINE_MENU
                elif self.menu_buttons[3].is_clicked(pos, click):  # Continue
                    if hasattr(self, "paused_board") and self.paused_board is not None:
                        self.board = self.paused_board
                        self.state = STATE_PLAYING
                        self.paused_board = None
                elif self.menu_buttons[4].is_clicked(pos, click):  # Quit
                    pygame.quit()
                    sys.exit()
                
    def handle_game_input(self, pos, click):
        """Handle input on the game screen"""
        # Update button hover states
        for button in self.game_buttons:
            button.check_hover(pos)
        # Handle button clicks
        if click:
            if self.game_buttons[0].is_clicked(pos, click):  # Menu
                # Disconnect if in online game
                if self.state == STATE_ONLINE_PLAYING and self.net:
                    self.net.send({'type': 'disconnect'})
                    self.net.close()
                    self.net = None
                else:
                    self.paused_board = self.board
                self.state = STATE_MENU
                return
            elif self.game_buttons[1].is_clicked(pos, click):  # Quit
                # Disconnect if in online game
                if self.state == STATE_ONLINE_PLAYING and self.net:
                    self.net.send({'type': 'disconnect'})
                    self.net.close()
                    self.net = None
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
                    # Only for local games
                    if not self.net:
                        self.reset_game()
                        self.state = STATE_PLAYING
                elif button.text == "Main Menu":
                    # Disconnect if in online game
                    if self.net:
                        self.net.send({'type': 'disconnect'})
                        self.net.close()
                        self.net = None
                    self.state = STATE_MENU
                elif button.text == "Quit":
                    # Disconnect if in online game
                    if self.net:
                        self.net.send({'type': 'disconnect'})
                        self.net.close()
                        self.net = None
                    pygame.quit()
                    sys.exit()

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
                        print(f"Opponent moved: {from_pos} -> {to_pos}")
                elif msg.get('type') == 'disconnect':
                    print("Opponent disconnected")
                    self.opponent_disconnected = True
                elif msg.get('type') == 'error':
                    print(f"Network error: {msg.get('message', 'Unknown error')}")
            return
        
        if self.player_color:
            # AI's turn to think
            if self.board.current_player != self.player_color:
                # Draw before AI moves
                self.draw_game()
                pygame.display.flip()
                engine.engine(self.board, self.board.current_player, type='alpha_beta', difficulty=self.ai_difficulty)
                # Draw after AI moves
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
                    # Clean disconnect
                    if self.net:
                        self.net.send({'type': 'disconnect'})
                        self.net.close()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                elif event.type == pygame.KEYDOWN and self.state == STATE_JOIN_INPUT:
                    if event.key == pygame.K_BACKSPACE:
                        self.ip_input = self.ip_input[:-1]
                        self.connection_error = None
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # Same as pressing Connect
                        host_ip = self.ip_input.strip()
                        if not host_ip:
                            self.connection_error = "Please enter an IP address"
                        else:
                            try:
                                self.net = NetworkConnection()
                                if self.net.connect(host_ip, DEFAULT_PORT):
                                    self.online_role = 'client'
                                    self.player_color = 'black'
                                    self.state = STATE_ONLINE_PLAYING
                                    self.board = Board()
                                    self.connection_error = None
                                    print(f"✓ Connected to {host_ip}:{DEFAULT_PORT}")
                                else:
                                    self.connection_error = "Connection failed. Check IP."
                                    self.net.close()
                                    self.net = None
                            except Exception as e:
                                self.connection_error = f"Error: {str(e)}"
                                if self.net:
                                    self.net.close()
                                    self.net = None
                    else:
                        ch = event.unicode
                        if ch and len(ch) == 1 and (ch.isdigit() or ch == '.' or ch == ':'):
                            self.ip_input += ch
                            self.connection_error = None

            # State machine
            if self.state == STATE_MENU:
                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)
            elif self.state in (STATE_SELECT_DIFFICULTY, STATE_ONLINE_MENU, STATE_HOST_WAITING, STATE_JOIN_INPUT):
                # ✅ Xử lý riêng cho HOST_WAITING: đọc message từ client
                if self.state == STATE_HOST_WAITING and self.net:
                    msg = self.net.get_message()
                    if msg:
                        print(f"[DEBUG] Host received message: {msg}")
                        if msg.get('type') == 'hello':
                            self.board = Board()
                            self.state = STATE_ONLINE_PLAYING
                            print("✓ Client connected via handshake! Game starting...")
                    elif self.net.connected.is_set():
                        # Đã accept socket nhưng chưa nhận hello
                        # (optional) print cho dễ debug
                        # print("Client connected (no handshake yet)... waiting for hello")
                        pass

                self.draw_menu()
                self.handle_menu_input(mouse_pos, mouse_clicked)

            elif self.state == STATE_PLAYING:
                self.update()
                self.draw_game()
                self.handle_game_input(mouse_pos, mouse_clicked)
            elif self.state == STATE_ONLINE_PLAYING:
                # Xử lý message từ đối thủ (move / disconnect / error)
                self.update()
                self.draw_game()

                if mouse_clicked:
                    # Lưu lại xem trước khi click có bao nhiêu nước
                    before = len(self.board.move_history)
                    # Kiểm tra xem trước khi click có phải tới lượt mình không
                    my_turn = (self.board.current_player == self.player_color)

                    # Luôn cho xử lý input (Menu, Quit, v.v.)
                    self.handle_game_input(mouse_pos, True)

                    after = len(self.board.move_history)

                    # Chỉ gửi nước đi nếu:
                    # - Trước đó đúng là lượt mình
                    # - Và sau khi click đã có thêm 1 nước mới trong move_history
                    if my_turn and after > before and self.net:
                        from_pos, to_pos, _, _ = self.board.move_history[-1]
                        self.net.send({'type': 'move', 'from': from_pos, 'to': to_pos})
                        print(f"Sent move: {from_pos} -> {to_pos}")

            elif self.state == STATE_GAME_OVER:
                self.draw_game()
                self.draw_game_over()
                self.handle_game_over_input(mouse_pos, mouse_clicked)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

           
# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()