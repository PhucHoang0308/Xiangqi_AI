# board.py: quản lý bàn cờ
import os
import sys
import pygame
from pieces.piece import Piece
import copy
class Board:
    # Game board constants
    WIDTH = 522
    HEIGHT = 630
    GRID_SIZE = 60
    PIECE_SIZE = 60
    MARGIN_LEFT = 35
    MARGIN_TOP = 100

    def __init__(self):
        # Initialize empty 10x9 board (rowx x cols)
        self.board = [[None for _ in range(9)] for _ in range(10)]
        self.current_player = 'red' # First player is red
        self.move_history = []
        self.selected_piece = None
        self.valid_moves = []
        
        # Load images
        self.load_images()
        
        # Set up pieces
        self.setup_pieces()

    def load_images(self):
        """Load all images needed for the game"""
        self.images = {}
        
        # Board background
        padding_top = 50
        self.images['board'] = pygame.image.load(os.path.join('src', 'res', 'bg.png')).convert()
        inner_padding = 20
        grid_image = pygame.image.load(os.path.join('src', 'res', 'grid.png')).convert_alpha()
        grid_width = self.WIDTH - 2*inner_padding
        grid_height = self.HEIGHT - 2*inner_padding - padding_top
        grid_image = pygame.transform.smoothscale(grid_image, (grid_width, grid_height))
        self.images['grid'] = grid_image
        

        piece_types = {
            'jiangshuai': {'red': 'red', 'black': 'black', 'type': 'jiang'},
            'shi': {'red': 'red', 'black': 'black', 'type': 'shi'},
            'xiang': {'red': 'red', 'black': 'black', 'type': 'xiang'},
            'ma': {'red': 'red', 'black': 'black', 'type': 'ma'},
            'ju': {'red': 'red', 'black': 'black', 'type': 'ju'},
            'pao': {'red': 'red', 'black': 'black', 'type': 'pao'},
            'bingzu': {'red': 'red', 'black': 'black', 'type': 'bingzu'},
        }

        # Piece icon
        # Tỉ lệ scale (để padding cho hình tròn không bị vỡ)
        scale_factor = 0.85
        scaled_size = self.PIECE_SIZE * scale_factor

        for piece_type, colors in piece_types.items():
            for color in ['red', 'black']:
                bg_name = colors[color]        # 'red' hoặc 'black'
                fg_name = colors['type']       # ví dụ: 'jiang'

                # Load background (vòng tròn nền màu)
                bg_path = os.path.join('src', 'res', f"{bg_name}icon.png")
                bg_image = pygame.image.load(bg_path).convert_alpha()
                bg_image = pygame.transform.smoothscale(bg_image, (scaled_size + 1, scaled_size + 1))

                # Load foreground (ký hiệu quân cờ)
                fg_path = os.path.join('src', 'res', f"{bg_name}{fg_name}.png")
                fg_image = pygame.image.load(fg_path).convert_alpha()
                fg_image = pygame.transform.smoothscale(fg_image, (self.PIECE_SIZE//2, self.PIECE_SIZE//2))

                # Tạo surface với kích thước chuẩn (có padding)
                piece_surface = pygame.Surface((self.PIECE_SIZE, self.PIECE_SIZE), pygame.SRCALPHA)
                offset = (self.PIECE_SIZE - scaled_size) // 2

                # Blit nền vào giữa
                piece_surface.blit(bg_image, (offset, offset))
                piece_surface.blit(fg_image, (self.PIECE_SIZE // 4, self.PIECE_SIZE // 4))

                # Lưu ảnh cuối cùng
                self.images[f"{color}_{piece_type}"] = piece_surface


        # UI elements
        self.images['select'] = pygame.image.load(os.path.join('src', 'res', 'select.png')).convert_alpha()
        self.images['select'] = pygame.transform.smoothscale(self.images['select'], (self.PIECE_SIZE, self.PIECE_SIZE))
        self.images['valid'] = pygame.image.load(os.path.join('src', 'res', 'valid.png')).convert_alpha()
        self.images['attack'] = pygame.image.load(os.path.join('src', 'res', 'attack.ico')).convert_alpha()
        self.images['attack'] = pygame.transform.smoothscale(self.images['attack'], (self.PIECE_SIZE, self.PIECE_SIZE))

    def setup_pieces(self):
        """Set up the initial board position with all pieces"""
        from pieces.jiang_shuai import JiangShuai
        from pieces.shi import Shi
        from pieces.xiang import Xiang
        from pieces.ma import Ma
        from pieces.ju import Ju
        from pieces.pao import Pao
        from pieces.bing_zu import BingZu
        
        # Place generals/kings
        self.place_piece(JiangShuai('black', (0, 4)))
        self.place_piece(JiangShuai('red', (9, 4)))
        
        # Place advisor/guards
        self.place_piece(Shi('black', (0, 3)))
        self.place_piece(Shi('black', (0, 5)))
        self.place_piece(Shi('red', (9, 3)))
        self.place_piece(Shi('red', (9, 5)))
        
        # Place elephant/bishops
        self.place_piece(Xiang('black', (0, 2)))
        self.place_piece(Xiang('black', (0, 6)))
        self.place_piece(Xiang('red', (9, 2)))
        self.place_piece(Xiang('red', (9, 6)))
        
        # Place horse/knights 
        self.place_piece(Ma('black', (0, 1)))
        self.place_piece(Ma('black', (0, 7)))
        self.place_piece(Ma('red', (9, 1)))
        self.place_piece(Ma('red', (9, 7)))
        
        # Place chariots/rooks
        self.place_piece(Ju('black', (0, 0)))
        self.place_piece(Ju('black', (0, 8)))
        self.place_piece(Ju('red', (9, 0)))
        self.place_piece(Ju('red', (9, 8)))
        
        # Place cannons
        self.place_piece(Pao('black', (2, 1)))
        self.place_piece(Pao('black', (2, 7)))
        self.place_piece(Pao('red', (7, 1)))
        self.place_piece(Pao('red', (7, 7)))
        
        # Place pawns/soldiers
        for i in range(0, 9, 2):
            self.place_piece(BingZu('black', (3, i)))
            self.place_piece(BingZu('red', (6, i)))

    def place_piece(self, piece):
        """Place a piece at its position on the board"""
        row, col = piece.position
        self.board[row][col] = piece
    
    def get_piece(self, position):
        """Get piece at the given position"""
        if position is None:
            return None
        row, col = position
        if 0 <= row < 10 and 0 <= col < 9:
            return self.board[row][col]
        return None
    
    def move_piece(self, from_pos, to_pos):
        """Move a piece and return captured piece."""
        piece = self.get_piece(from_pos)
        if piece is None or (to_pos not in piece.get_valid_moves(self)):
            return None

        captured_piece = self.get_piece(to_pos)

        self.board[from_pos[0]][from_pos[1]] = None
        self.board[to_pos[0]][to_pos[1]] = piece
        piece.position = to_pos

        self.current_player = 'black' if self.current_player == 'red' else 'red'
        
        self.move_history.append((from_pos, to_pos, piece, captured_piece))

        self.selected_piece = None
        self.valid_moves = []

        return captured_piece

    def undo_move(self, from_pos, to_pos, captured_piece):
        """Undo a move."""
        piece = self.get_piece(to_pos)
        if piece is None:
            return False

        self.board[from_pos[0]][from_pos[1]] = piece
        self.board[to_pos[0]][to_pos[1]] = captured_piece
        piece.position = from_pos

        self.current_player = 'black' if self.current_player == 'red' else 'red'
        
        if self.move_history:
            self.move_history.pop()

        self.selected_piece = None
        self.valid_moves = []

        return True

    
    def is_in_check(self, color):
        """Check if the player of given color is in check (bị chiếu tướng)"""
        # pind the generals/king
        king_pos  = next(((row, col) for row in range(10) for col in range(9) 
                            if (self.board[row][col]
                            and self.board[row][col].color == color 
                            and self.board[row][col].__class__.__name__ == 'JiangShuai')), None)
        
        if king_pos is None: return False
        
        # Check if any opponent piece can capture the king
        opposite_color = 'black' if color == 'red' else 'red'
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.color == opposite_color:
                    if king_pos in piece.get_valid_moves(self):
                        return True
        return False

    def is_checkmate(self, color):
        """Check if the player of given color is in checkmate."""
        valid_moves = self.get_legal_moves(color)
        if not valid_moves:
            # Nếu không còn nước đi hợp lệ, chỉ checkmate nếu đang bị chiếu
            return self.is_in_check(color)
        if not self.is_in_check(color):
            return False
        # Thử tất cả nước đi để xem có nước nào thoát khỏi chiếu không
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_valid_moves(self):
                        original_pos = piece.position
                        captured = self.get_piece(move)
                        self.board[original_pos[0]][original_pos[1]] = None
                        self.board[move[0]][move[1]] = piece
                        piece.position = move
                        still_in_check = self.is_in_check(color)
                        self.board[original_pos[0]][original_pos[1]] = piece
                        piece.position = original_pos
                        self.board[move[0]][move[1]] = captured
                        if not still_in_check:
                            return False
        # Nếu không có nước nào thoát khỏi chiếu thì đúng là checkmate
        return True

    def is_game_over(self):
        """Check if the game is over (checkmate)"""
        return self.is_checkmate('red') or self.is_checkmate('black')
    
    def get_legal_moves(self, color):
        """Get all legal moves for the player of given color"""
        moves = []
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_valid_moves(self):
                        # Only include that dont leave the player in check
                        original_pos = piece.position
                        captured = self.get_piece(move)
                        
                        self.board[original_pos[0]][original_pos[1]] = None
                        self.board[move[0]][move[1]] = piece
                        piece.position = move
                        
                        # Check if the move leaves the player in check
                        in_check = self.is_in_check(color)
                        
                        # Undo the move
                        self.board[original_pos[0]][original_pos[1]] = piece
                        piece.position = original_pos
                        self.board[move[0]][move[1]] = captured
                        
                        if not in_check:
                            moves.append((original_pos, move)) # ((r, c), (r, c))
        return moves
    
    def screen_to_board(self, screen_pos):
        """Convert screen coordinates to board position"""
        x, y = screen_pos
        # Adjust for margin
        x -= self.MARGIN_LEFT
        y -= self.MARGIN_TOP

        # Calculate board position
        col = round(x / self.GRID_SIZE)
        row = round(y / self.GRID_SIZE)

        # Check if within board bounds
        if 0 <= row < 10 and 0 <= col < 9:
            return (row, col)
        return None

    def board_to_screen(self, board_pos):
        """Convert board position to screen coordinates"""
        row, col = board_pos
        x = self.MARGIN_LEFT + col * self.GRID_SIZE
        y = self.MARGIN_TOP + row * self.GRID_SIZE
        return (x, y)

    def select_piece(self, position):
        """Select a piece on the board"""
        piece = self.get_piece(position)
        if piece and piece.color == self.current_player:
            self.selected_piece = piece
            self.valid_moves = []
            # Calculate valid moves that don't leave player in check
            for move in piece.get_valid_moves(self):
                # Temporarily make the move
                original_pos = piece.position
                captured = self.get_piece(move)

                self.board[original_pos[0]][original_pos[1]] = None
                self.board[move[0]][move[1]] = piece
                piece.position = move
                
                # Check if the move leaves the player in check
                in_check = self.is_in_check(piece.color)
                
                # Undo the move
                self.board[original_pos[0]][original_pos[1]] = piece
                piece.position = original_pos
                self.board[move[0]][move[1]] = captured
                
                if not in_check:
                    self.valid_moves.append(move)
            return True
        return False
        
    def handle_click(self, pos):
        """Handle a click on the board"""
        board_pos = self.screen_to_board(pos)
        if not board_pos:
            return False

        # If a piece is already selected
        if self.selected_piece:
            # Try to move the selected piece to the clicked position
            if board_pos in self.valid_moves:
                return self.move_piece(self.selected_piece.position, board_pos)
            else:
                # Try to select another piece
                new_piece = self.get_piece(board_pos)
                if new_piece and new_piece.color == self.current_player:
                    self.select_piece(board_pos)
                    return True
                # Deselect if clicking on empty square or opponent's piece
                self.selected_piece = None
                self.valid_moves = []
                return True
        else:
            # Try to select a piece
            return self.select_piece(board_pos)
    def handle_AI_move(self, from_pos, to_pos):
        self.select_piece(from_pos)
        if to_pos in self.valid_moves:
            return self.move_piece(from_pos, to_pos)
        self.selected_piece = None
        self.valid_moves = []
        return False

    def draw(self, screen):
        """Draw the board and pieces on the screen"""
        # Draw the board background
        screen.blit(self.images['board'], (0, 0))
        screen.blit(self.images['grid'], (self.MARGIN_LEFT, self.MARGIN_TOP))

        # Draw highlights for selected piece and valid moves
        if self.selected_piece:
            # Highlight selected piece
            pos = self.board_to_screen(self.selected_piece.position)
            screen.blit(self.images['select'], (pos[0] - self.PIECE_SIZE // 2, pos[1] - self.PIECE_SIZE // 2))

            # Highlight valid moves
            for move in self.valid_moves:
                pos = self.board_to_screen(move)
                # Use attack icon if there's an opponent's piece, otherwise valid move icon
                if self.get_piece(move) and self.get_piece(move).color != self.current_player:
                    screen.blit(self.images['attack'], (pos[0] - self.PIECE_SIZE // 2, pos[1] - self.PIECE_SIZE // 2))
                else:
                    screen.blit(self.images['valid'], (pos[0] - 12, pos[1] - 12))

        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    # Get the correct image for this piece
                    piece_type = piece.__class__.__name__.lower()
                    image_key = f"{piece.color}_{piece_type}"
                    if image_key in self.images:
                        pos = self.board_to_screen((row, col))
                        screen.blit(self.images[image_key], (pos[0] - self.PIECE_SIZE // 2, pos[1] - self.PIECE_SIZE // 2))
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if is_surface(v):
                setattr(result, k, v)  # dùng lại reference
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result
    def copy(self):
        return copy.deepcopy(self)
    def is_repeating_state(self, color='red', repeat_limit=3):
        if len(self.move_history) < repeat_limit * 2:
            return False

        # Lấy các nước đi của màu đang xét
        filtered = [(f, t) for f, t, piece, _ in self.move_history if piece.color == color]
        
        if len(filtered) < repeat_limit * 2:
            return False

        recent = filtered[-repeat_limit*2:]
        return all(recent[i] == recent[i+2] for i in range(0, repeat_limit*2 - 2, 2))
    def get_total_moves(self):
        """Trả về tổng số nước đi đã diễn ra trong game"""
        return len(self.move_history)
    def is_threefold_repetition(self, color: str) -> bool:
        """
        Kiểm tra tam chiếu (3 lần chiếu liên tiếp mà không thay đổi trạng thái).
        - color: màu của người kiểm tra ('red' hoặc 'black')
        """
        if len(self.move_history) < 6:
            return False  # Chưa đủ nước đi để lặp

        # Lấy 6 nước gần nhất (3 lần đi mỗi bên)
        recent_moves = self.move_history[-6:]

        # Kiểm tra xem có phải người này cứ chiếu liên tục không
        for i in range(0, 6, 2):
            from_pos, to_pos, piece, captured = recent_moves[i]
            if piece.color != color:
                return False  # Không phải người cần xét đi, bỏ qua

            # Kiểm tra nước đi này có chiếu không
            temp_board = self.copy()
            temp_piece = temp_board.get_piece(from_pos)
            temp_board.board[from_pos[0]][from_pos[1]] = None
            temp_board.board[to_pos[0]][to_pos[1]] = temp_piece
            if temp_piece:
                temp_piece.position = to_pos
            if not temp_board.is_in_check('black' if color == 'red' else 'red'):
                return False  # Nếu nước này không chiếu tướng thì không phải tam chiếu

        return True  # Nếu 3 lần chiếu liên tiếp thì đúng là tam chiếu




def is_surface(obj):
    if isinstance(obj, pygame.Surface):
        return True
    if isinstance(obj, (list, tuple, set)):
        return any(is_surface(item) for item in obj)
    if isinstance(obj, dict):
        return any(is_surface(k) or is_surface(v) for k, v in obj.items())
    return False