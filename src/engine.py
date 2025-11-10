from board.board import Board
from search import alphabeta, minimax, iterative_deepening
def engine(board: Board,Ai_color:str,type = 'minimax', difficulty = 2):
    """
    This function is the main engine for AI chess game with many types of AI.
    The default setiing is Alpha-beta.
    The default difficulty is 2. (1-3)
        Otherwise, difficulty also set the depth of the search tree."""
    if type == 'alpha_beta':
        alpha_beta = alphabeta.AlphaBeta()
        maximizing = (board.current_player == Ai_color)
        
        best_move = alpha_beta.search(board, depth=difficulty, is_maximizing=maximizing, alpha=float('-inf'), beta=float('inf'))
        #print(f"pruned_branches: {alpha_beta.pruned_branches} branches pruned")
        #print(f"Time taken: {alpha_beta.time_taken:.2f} seconds")
        #print(f"Total_nodes: {alpha_beta.total_nodes} nodes searched")
    elif type == 'minimax':
        # Minimax algorithm without pruning
        m = minimax.Minimax()
        maximizing = (board.current_player == Ai_color)
        best_move = m.search(board, depth=difficulty, is_maximizing=maximizing)
        #print(f"Time taken: {m.time_taken:.2f} seconds")
        #print(f"Total_nodes: {m.total_nodes} nodes searched")
    elif type == 'iterative_deepening':
        # Iterative deepening search algorithm
        best_move = iterative_deepening.iterative_deepening_search(board, max_depth=difficulty, time_limit=50.0)
    else:
        raise ValueError("Invalid AI type. Use 'alpha_beta' or 'minimax'.")
    if best_move != (None, None, float('-inf')) and best_move[0] is not None and best_move[1] is not None:
        board.handle_AI_move(best_move[0], best_move[1])
    else:
        # Không còn nước đi, để game tự xử lý kết thúc
        return