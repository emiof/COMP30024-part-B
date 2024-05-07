from t_board import TBoard
from ..referee.game.actions import Action
from ..referee.game.player import PlayerColor


def best_next_move() -> Action:
    if depth == 0:
        return t_
    playable_tetrominos: list[Tetromino] = t_board.playable_tetrominos(curr_player)

    if depth ==not playable_tetrominos or t_board.max_turn_reached():
        return t_board.player_score(main_player)
    elif depth == 0:
        return t_board.predict_player_score(main_player)
    
    
    

    
    