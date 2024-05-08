from ..referee.game.constants import BOARD_N
from ..referee.game.coord import Coord

def row_coords(row: int) -> list[Coord]:
    if row >= BOARD_N or row < 0:
        raise Exception("Invalid row value")
    
    return [Coord(row, col) for col in range(BOARD_N)]

def col_coords(col: int) -> list[Coord]:
    if col >= BOARD_N or col < 0:
        raise Exception("Invalid row value")
    
    return [Coord(row, col) for row in range(BOARD_N)]

def minimax_depth(time_remaining: float, space_remaining: float) -> int:
    return 100