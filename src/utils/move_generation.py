"""
API chuẩn hóa cho sinh nước đi và đánh giá bàn cờ. Chỉ dùng file này cho AI/game logic, tránh dùng các bản cũ như temp.py.
"""
from board.board import Board
from evaluation.shi_zhi import ShiZhi

def get_chess_of_color(color: str) -> list:
    if color == 'red':
        return ['R', 'M', 'X', 'S', 'J', 'P', 'B']
    elif color == 'black':
        return ['r', 'm', 'x', 's', 'j', 'p', 'b']
    else:
        raise ValueError("Invalid color. Use 'red' or 'black'.")

def get_valid_moves(board: Board, AI_color: str) -> list:
    board_map = board.board
    valid_moves = []
    AI_chess = get_chess_of_color(AI_color)

    for row in range(10):
        for col in range(9):
            piece = board_map[row][col]
            if piece is None or piece.symbol not in AI_chess:
                continue

            raw_moves = piece.get_valid_moves(board)
            filtered_moves = []

            for move in raw_moves:
                from_pos = piece.position
                captured = board.move_piece(from_pos, move)
                
                if not board.is_in_check(AI_color):
                    filtered_moves.append(move)
                
                board.undo_move(from_pos, move, captured)

            if filtered_moves:
                valid_moves.append((piece, filtered_moves))

    return valid_moves

def list1_2list(valid_moves: list) -> list:
    """
    Convert [(piece, [move1, move2, ...]), ...] to [(piece, move1), (piece, move2), ...]
    """
    result = []
    for piece, moves in valid_moves:
        for move in moves:
            result.append((piece, move))
    return result

def evaluation_board(board: Board, evaluating_color: str) -> int:
    """
    Evaluate board for given color.
    """
    opponent = 'black' if evaluating_color == 'red' else 'red'
    if board.is_checkmate(evaluating_color):
        return -99999999
    if board.is_checkmate(opponent):
        return 99999999
    if board.is_repeating_state(evaluating_color):
        return -99999

    return (
        checkShizhi(board, evaluating_color)
        + checkShizhan(board, evaluating_color)
        + checkKongjian(board, evaluating_color)
    )

def checkShizhi(board: Board, evaluating_color: str) -> int:
    AI_chess = get_chess_of_color(evaluating_color)
    piece_value = ShiZhi()
    value_AI, value_Opp = 0, 0

    for row in board.board:
        for piece in row:
            if piece is None:
                continue
            if piece.symbol in AI_chess:
                value_AI += piece_value.get_value(piece)
            else:
                value_Opp += piece_value.get_value(piece)

    return value_AI - value_Opp

def checkShizhan(board: Board, evaluating_color: str) -> int:
    score = 0
    for row in board.board:
        for piece in row:
            if piece and piece.color == evaluating_color:
                r, _ = piece.position
                if piece.__class__.__name__.lower() in ['ma', 'ju', 'pao']:
                    if (evaluating_color == 'red' and r < 5) or (evaluating_color == 'black' and r > 4):
                        score += 5
    return score

def checkKongjian(board: Board, evaluating_color: str) -> int:
    total_valid_moves_AI = 0
    total_valid_moves_opp = 0
    AI_chess = get_chess_of_color(evaluating_color)

    for row in board.board:
        for piece in row:
            if piece is None:
                continue
            moves = piece.get_valid_moves(board)
            if piece.symbol in AI_chess:
                total_valid_moves_AI += len(moves)
            else:
                total_valid_moves_opp += len(moves)

    return (total_valid_moves_AI - total_valid_moves_opp) * 100
