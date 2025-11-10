
# Tệp này định nghĩa quân Jiang/Shuai (Tướng) trong cờ Tướng (Xiangqi).
from pieces.piece import Piece
from board.palace import is_in_palace
import sys

class JiangShuai(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'J' if color == 'red' else 'j'
        
    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        
        # The general can move one step orthogonally (not diagonally)
        possible_moves = [
            (row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)
        ]
        
        for move in possible_moves:
            # Check if move is within the palace
            if not is_in_palace(move, self.color):
                continue
            
            # Check if destination has friendly piece
            piece_at_dest = board.get_piece(move)
            if piece_at_dest and piece_at_dest.color == self.color:
                continue
            
            moves.append(move)

        # Luật "tướng đối mặt" chỉ dùng để kiểm tra chiếu, không phải nước đi hợp lệ của tướng
        return moves