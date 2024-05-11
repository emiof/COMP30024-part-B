from referee.game.coord import Coord
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N, MAX_TURNS
from .tetromino import Tetromino
from .t_board_counter import TBoardCounter
from .utils import row_coords, col_coords
import numpy as np

class TBoard:
    def __init__(
        self,
        board: dict[Coord, PlayerColor] = {},
        turn_count: int = 0,
        player_playable_tetrominos: dict[PlayerColor, set[Tetromino]] = {PlayerColor.RED: set(), PlayerColor.BLUE: set()},
        t_board_counter: TBoardCounter = TBoardCounter(),
    ):
        self.board: dict[Coord, PlayerColor] = board
        self.turn_count: int = turn_count
        self.player_playable_tetrominos: dict[PlayerColor, set[Tetromino]] = player_playable_tetrominos
        self.t_board_counter: TBoardCounter = t_board_counter   
    
    def any_playable_tetromino(self) -> Tetromino:
        for row in range(BOARD_N):
            for col in range(BOARD_N):
                curr_coord: Coord = Coord(row, col)
                if curr_coord not in self.board:
                    for tetromino in Tetromino.all_tetrominos_at(curr_coord):
                        if self.__can_place_tetromino(tetromino):
                            return tetromino

    def playable_tetrominos(self, player: PlayerColor) -> list[Tetromino]:
        return list(self.player_playable_tetrominos[player])
    
    def max_turn_reached(self) -> bool:
        return self.turn_count == MAX_TURNS

    def player_score(self, player: PlayerColor) -> float:
        if self.max_turn_reached():
            player_tokens: int = self.num_tokens(player)
            opponent_tokens: int = self.num_tokens(player.opponent)
            return float('inf') if player_tokens > opponent_tokens else float('-inf') if player_tokens < opponent_tokens else 0
        elif not self.player_playable_tetrominos[player] or not self.player_playable_tetrominos[player.opponent]:
            return float('-inf') if not self.player_playable_tetrominos[player] else float('inf')

        return len(self.player_playable_tetrominos[player]) - len(self.player_playable_tetrominos[player.opponent])
    
    def copy(self) -> 'TBoard':
        return TBoard(self.board.copy(), self.turn_count, self.player_playable_tetrominos.copy(), self.t_board_counter.copy())
    
    def num_tokens(self, player: PlayerColor) -> float:
        return sum([1 for _player in self.board.values() if _player == player])

    def place_tetromino_in_place(self, tetromino: Tetromino, player: PlayerColor) -> None:
        for token in tetromino.tokens:
            if token in self.board:
                raise Exception("Placing token in occupied coordinate")
            
            self.board[token] = player

        self.turn_count += 1

        removed_rows, removed_cols = self.t_board_counter.place_tetromino(tetromino)
        self.__remove_rows(removed_rows)
        self.__remove_cols(removed_cols)

        self.__update_playable_tetrominos()

    def place_tetromino(self, tetromino: Tetromino, player: PlayerColor) -> 'TBoard':
        t_board_copy: 'TBoard' = TBoard(self.board.copy(), self.turn_count, self.player_playable_tetrominos.copy(), self.t_board_counter.copy())
        t_board_copy.place_tetromino_in_place(tetromino, player)

        return t_board_copy
 
    def __update_playable_tetrominos(self) -> None:
        self.player_playable_tetrominos[PlayerColor.BLUE] = self.__find_playable_tetrominos(PlayerColor.BLUE)
        self.player_playable_tetrominos[PlayerColor.RED] = self.__find_playable_tetrominos(PlayerColor.RED)

    def __find_playable_tetrominos(self, player: PlayerColor) -> set[Tetromino]:
        tetrominos: set[Tetromino] = set()

        for row in range(BOARD_N):
            for col in range(BOARD_N):
                curr_coord: Coord = Coord(row, col)
                if curr_coord not in self.board and self.__has_adj_token(curr_coord, player):
                    for tetromino in Tetromino.all_tetrominos_at(curr_coord):
                        if tetromino not in tetrominos and  self.__can_place_tetromino(tetromino):
                            tetrominos.add(tetromino)

        return tetrominos
    
    def __can_place_tetromino(self, tetromino: Tetromino) -> bool:
        return all(coord not in self.board for coord in tetromino.tokens)
    
    def __has_adj_token(self, coord: Coord, player: PlayerColor) -> bool:
        return any(self.board[_coord] == player for _coord in [coord.up(), coord.down(), coord.right(), coord.left()] if _coord in self.board)
    
    def __remove_rows(self, rows: list[int]) -> None:
        for row_index in rows:
            for coord in row_coords(row_index):
                if coord in self.board:
                    del self.board[coord]

    def __remove_cols(self, cols: list[int]) -> None:
        for col_index in cols:
            for coord in col_coords(col_index):
                if coord in self.board:
                    del self.board[coord]

    @staticmethod
    def create_board_id(t_board: 'TBoard') -> int:
        compute_board_position = lambda row, col: row * BOARD_N + col
        board_positions: np.ndarray = np.zeros(BOARD_N * BOARD_N)

        for coord, player in t_board.board.items():
            board_positions[compute_board_position(coord.r, coord.c)] = 2 if player == PlayerColor.RED else 1

        return hash(tuple(board_positions))