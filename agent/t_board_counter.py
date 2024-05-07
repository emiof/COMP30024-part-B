from .tetromino import Tetromino
from ..referee.game.player import PlayerColor
from ..referee.game.coord import Coord
from ..referee.game.constants import BOARD_N

class TBoardCounter:
    def __init__(self, row_counts: list[int] | None = None, col_counts: list[int] | None = None):
        self.row_counts: list[int] = row_counts if row_counts != None else [0 for _ in range(BOARD_N)]
        self.col_counts: list[int] = col_counts if col_counts != None else [0 for _ in range(BOARD_N)]

    def place_tetromino(self, tetromino: Tetromino, player: PlayerColor) -> tuple[list[int], list[int]]:
        for token in tetromino:
            self.row_counts[token.r] += 1
            self.col_counts[token.c] += 1

        if self.row_counts[token.r] > BOARD_N or self.col_counts[token.c] > BOARD_N:
            raise Exception("Invalid tetromino placement")
        
        removed_rows, removed_cols = self.__perform_line_removals()
        return removed_rows, removed_cols

    def copy(self) -> 'TBoardCounter':
        return TBoardCounter(self.row_counts.copy(), self.col_counts.copy())
    
    def __perform_line_removals(self) -> tuple[list[int], list[int]]:
        complete_rows: list[int] = [i for (i, row_count) in self.row_counts if row_count == BOARD_N]
        complete_cols: list[int] = [i for (i, col_count) in self.col_counts if col_count == BOARD_N]

        for (row, col) in zip(complete_rows, complete_cols):
            self.row_counts[row] = 0
            self.col_counts[col] = 0

        self.row_counts = [0 if row_count - len(complete_cols) < 0 else row_count - len(complete_cols) for row_count in self.row_counts]
        self.col_counts = [0 if col_count - len(complete_rows) < 0 else col_count - len(complete_rows) for col_count in self.col_counts]

        return complete_rows, complete_cols




