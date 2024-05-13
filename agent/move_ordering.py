from enum import Enum
from .tetromino import Tetromino
from referee.game.player import PlayerColor
from referee.game.board import Coord
from .misc import coord_adjacents

class DesirabilityMetric(Enum):
    OPPONENT_ADJ_TOKENS = 1
    EMPTY_ADJ_DIFFERENCE = 2

def calculate_move_desirability(board: dict[Coord, PlayerColor], tetromino: Tetromino, player: PlayerColor, desirability_metric: DesirabilityMetric) -> float:
    match desirability_metric:
        case DesirabilityMetric.OPPONENT_ADJ_TOKENS:
            return opponent_adj_tokens(board, tetromino, player)
        case DesirabilityMetric.EMPTY_ADJ_DIFFERENCE:
            return empty_adj_difference(board, tetromino, player)

def opponent_adj_tokens(board: dict[Coord, PlayerColor], tetromino: Tetromino, player: PlayerColor) -> float:
    return sum([1 for adj_coord in tetromino.all_adj_coords() if adj_coord in board and board[adj_coord] == player.opponent])

def empty_adj_difference(board: dict[Coord, PlayerColor], tetromino: Tetromino, player: PlayerColor) -> float:
    board_copy: dict[Coord, PlayerColor] = board.copy()
    for token in tetromino.tokens:
        board_copy[token] = player
    
    players_empty_adj_coords: dict[PlayerColor, set[Coord]] = {PlayerColor.BLUE: set(), PlayerColor.RED: set()}

    for coord, player_color in board_copy.items():
        players_empty_adj_coords[player_color].update([adj_coord for adj_coord in coord_adjacents(coord) if adj_coord not in board_copy])

    return len(players_empty_adj_coords[player]) - len(players_empty_adj_coords[player.opponent])