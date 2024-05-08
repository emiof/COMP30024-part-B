from ..referee.game import PlayerColor
from .t_board import TBoard
from .tetromino import Tetromino
from ..referee.game.actions import Action

def best_next_move(
    t_board: TBoard,
    curr_player: PlayerColor,
    main_player: PlayerColor,
    alpha: float,
    beta: float,
    depth: int
) -> tuple[float, Tetromino | None]:
    """
    Utilizes the minimax algorithm with alpha-beta pruning and a depth limit, to identify the move by the current player,
    at the current board state, which leads to a maximized utility. 
    """
    playable_tetrominos: list[Tetromino] = t_board.playable_tetrominos(curr_player)

    if depth == 0 or t_board.max_turn_reached() or not playable_tetrominos: 
        # Reached max depth, terminal state, or a state where the current player can't make any moves. 
        return t_board.player_score(main_player), None 
    
    if (curr_player == main_player): # Maximizing 
        max_utility: float = float('-inf')
        max_utility_move: Tetromino | None = None 

        for tetromino in playable_tetrominos:
            utility, _ = best_next_move(t_board.place_tetromino(tetromino, curr_player), curr_player.opponent(), main_player, alpha, beta, depth - 1)
            
            if utility > max_utility:
                max_utility, max_utility_move = utility, tetromino

            if max_utility > beta:
                return max_utility, max_utility_move

            alpha = max(max_utility, alpha)

        return max_utility, max_utility_move
    else: # Minimizing  
        min_utility = float('inf')
        min_utility_move: Tetromino | None = None

        for tetromino in playable_tetrominos:
            utility, _ = best_next_move(t_board.place_tetromino(tetromino, curr_player), curr_player.opponent(), main_player, alpha, beta, depth - 1)

            if utility < min_utility:
                min_utility, min_utility_move = utility, tetromino

            if min_utility < alpha:
                return min_utility, min_utility_move
            
            beta = min(min_utility, beta)
            
        return min_utility, min_utility_move
    
