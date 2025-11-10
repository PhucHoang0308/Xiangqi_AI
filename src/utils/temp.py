"""
TODO: File này là bản cũ/trùng lặp của move_generation.py. Khuyến nghị chỉ dùng src/utils/move_generation.py cho logic chính.
"""

import sys
import os
from board.board import Board
import copy
from evaluation.shi_zhi import ShiZhi
def get_chess_of_color(color: str) -> list:
    """
    Get the chess pieces of a specific color.
    
    :param color: The color of the chess pieces ('red' or 'black').
    :return: A list of chess pieces of the specified color.
    """
    if color == 'red':
        return ['R','M','X','S','J','P','B']
    elif color == 'black':
        return ['r','m','x','s','j','p','b']
    else:
        raise ValueError("Invalid color. Use 'red' or 'black'.")
def get_valid_moves(board: Board, AI_color: str) -> list:
    board_map = board.board
    valid_move = []
    AI_chess = get_chess_of_color(AI_color)
    
    for i in board_map:
        for j in i:
            if j is None:
                continue
            if j.symbol in AI_chess:
                raw_moves = j.get_valid_moves(board)
                filtered_moves = []
                for move in raw_moves:
                    if is_move_legal(board, j, move):
                        filtered_moves.append(move)
                if filtered_moves:
                    valid_move.append((j, filtered_moves))
    return valid_move

def evaluate_generation(board: Board, valid_move:list)->list:
    """
    This func generates the point of the move for each piece without exception.
    Otherwise, it follow the: 
        Shizhi - the value of the piece.
        Shizhan - the value of the position.
        Kongjian - the value of the space.
    The output is list [piece,[(move1,value),(move2,value),...]]
    """
    result = []
    for piece, moves in valid_move:
        temp = []
        for move in moves:
            board_copy = board.copy()  # Create a copy of the board to simulate the move
            board_copy.move_piece(piece.position, move)  # Simulate the move on the copy
            # Calculate the value of the move based on the piece, position, and space
            shizhi_value = checkShizhi(board_copy)
            shizhan_value = checkShizhan(board_copy)
            kongjian_value = checkKongjian(board_copy)
            
            # Combine the values to get a final score for the move
            total_value = shizhi_value + shizhan_value + kongjian_value
            
            # Append the result for this piece and move
            temp.append((move, total_value))
         #Sort the moves by value for faster Pruning in Apha-Beta.
        result.append((piece,temp))
    return result
def checkShizhi (board:Board)->int:
    """
    This func check the value of the piece.
    The value may be too high, so the return should be (Value_AI_chess - Value_player_chess).
    """
    AI_chess = get_chess_of_color(board.current_player)
    piece_value = ShiZhi()
    value_AI = 0
    value_Player = 0
    for i in board.board:
        for j in i:
            if j is None:
                continue
            if j.symbol in AI_chess:
                value_AI += piece_value.get_value(j)
            else:
                value_Player += piece_value.get_value(j)
    if board.is_checkmate(board.current_player):

            value_Player -= 10000
            value_AI += 10000
    if board.is_in_check(board.current_player):
            value_Player += 10000
            value_AI -= 10000
    value = value_AI - value_Player
    return value
def checkShizhan (board:Board)->int:
    """
    This func check the value of the position.
    This func is really important, because it check the value of tactics and pos.
    This func check some pos of some pieces and some of tactics which dev added.
    """

    return 0
def checkKongjian (board:Board)->int:
    """
    This func check the value of the space.
    There are some terms in this func:
        - The number of valid moves in the position.
        - The number of valid moves of the enemy in the position.
    Otherwise, there are still more custom terms:
        - Check if piece is in Deadlock (with xiang this is checkmate).
    """
    total_valid_moves_AI = 0
    total_valid_moves_player = 0
    AI_chess = get_chess_of_color(board.current_player)
    for i in board.board:
        for j in i:
            if j is None:
                continue
            if j.symbol in AI_chess:
                total_valid_moves_AI += len(j.get_valid_moves(board))
            else:
                total_valid_moves_player += len(j.get_valid_moves(board))
    Deadlock = CheckDeadLock(board)
    deadlockvalue=0
    if Deadlock >0:
        deadlockvalue = -100 * Deadlock
    return (total_valid_moves_AI - total_valid_moves_player)*100 + deadlockvalue

def CheckDeadLock(board:Board)->int:
    """
    This func check if the piece is in deadlock.
    The deadlock is the situation that the piece can not move to any position.
    """
    AI_chess = get_chess_of_color(board.current_player)
    number_DL = 0
    for i in board.board:
        for j in i:
            if j is None:
                continue
            if j.symbol in AI_chess:
                if len(j.get_valid_moves(board)) == 0:
                    number_DL += 1
    return number_DL
def list1_2list(valid_move:list)->list:

    """
    This func convert the list from (piece,[(move1,value),(move2,value),...]) to [(piece,move1,value1),(piece,move2,value2),...]
    """
    result = []
    for piece, moves in valid_move:
        for move, value in moves:
            result.append((piece, move, value))
    return result

def evaluation_board(board:Board)->int:
    """
    This func evaluate the board and return the value of the board.
    The value is the sum of the value of all pieces on the board.
    """
    player_color = 'red' if board.current_player == 'black' else 'black'
    if board.is_checkmate(board.current_player):
        return -99999999
    if board.is_checkmate(player_color):
        return 99999999
    shizhi_value = checkShizhi(board)
    shizhan_value = checkShizhan(board)
    kongjian_value = checkKongjian(board)
            
            # Combine the values to get a final score for the move
    total_value = shizhi_value + shizhan_value + kongjian_value


    return total_value
def is_move_legal(board: Board, piece, move) -> bool:
    """Check if a move is legal (does not leave own king in check)"""
    original_pos = piece.position
    captured_piece = board.get_piece(move)
    
    # Make the move
    board.board[original_pos[0]][original_pos[1]] = None
    board.board[move[0]][move[1]] = piece
    piece.position = move

    # Check if in check
    in_check = board.is_in_check(piece.color)

    # Undo move
    board.board[original_pos[0]][original_pos[1]] = piece
    piece.position = original_pos
    board.board[move[0]][move[1]] = captured_piece

    return not in_check
