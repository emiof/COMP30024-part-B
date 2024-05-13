from referee.game.coord import Coord
from referee.game.player import PlayerColor
from referee.game.constants import BOARD_N, MAX_TURNS
from .tetromino import Tetromino
from .t_board_counter import TBoardCounter
from .misc import row_coords, col_coords, all_board_coords
from .move_ordering import calculate_move_desirability, DesirabilityMetric
import numpy as np
from typing import Callable

class TBoard:
    def __init__(
        self,
        board: dict[Coord, PlayerColor] = {},
        turn_count: int = 0,
        player_num_tokens: dict[PlayerColor, int] = {PlayerColor.RED: 0, PlayerColor.BLUE: 0},
        player_playable_tetrominos: dict[PlayerColor, set[Tetromino]] = {PlayerColor.RED: set(), PlayerColor.BLUE: set()},
        t_board_counter: TBoardCounter = TBoardCounter(),
    ):
        self.board: dict[Coord, PlayerColor] = board
        self.turn_count: int = turn_count
        self.player_num_tokens = player_num_tokens
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

    def playable_tetrominos(self, player: PlayerColor, sort: bool, remove_similar: bool) -> list[Tetromino]:
        if sort:
            find_desirability: Callable[[Tetromino], tuple[Tetromino, float]] = lambda tetro: (tetro, self.tetromino_desirability(tetro, player))
            key = lambda elem: elem[1]

            sorted_tetrominos: list[tuple[Tetromino, float]] = sorted(list(map(find_desirability, self.player_playable_tetrominos[player])), reverse=True, key=key)

            if remove_similar:
                sorted_tetrominos = [sorted_tetrominos[i] for i in range(len(sorted_tetrominos)) if i == 0 or sorted_tetrominos[i][1] != sorted_tetrominos[i-1][1]]

            return [tetromino for tetromino, _ in sorted_tetrominos]
        else:
            return list(self.player_playable_tetrominos[player])
    
    def max_turn_reached(self) -> bool:
        return self.turn_count == MAX_TURNS

    def player_score(self, player: PlayerColor) -> float:
        if self.max_turn_reached():
            player_tokens: int = self.player_num_tokens[player]
            opponent_tokens: int = self.player_num_tokens[player.opponent]
            return float('inf') if player_tokens > opponent_tokens else float('-inf') if player_tokens < opponent_tokens else 0
        elif not self.player_playable_tetrominos[player] or not self.player_playable_tetrominos[player.opponent]:
            return float('-inf') if not self.player_playable_tetrominos[player] else float('inf')

        return len(self.player_playable_tetrominos[player]) - len(self.player_playable_tetrominos[player.opponent])
    
    def copy(self) -> 'TBoard':
        return TBoard(self.board.copy(), self.turn_count, self.player_num_tokens.copy(), self.player_playable_tetrominos.copy(), self.t_board_counter.copy())
    
    def place_tetromino_in_place(self, tetromino: Tetromino, player: PlayerColor) -> None:
        for token in tetromino.tokens:
            if token in self.board:
                raise Exception("Placing token in occupied coordinate")
            
            self.board[token] = player

        self.turn_count += 1
        self.player_num_tokens[player] += 4 

        removed_rows, removed_cols = self.t_board_counter.place_tetromino(tetromino)
        self.__remove_rows(removed_rows)
        self.__remove_cols(removed_cols)

        self.__update_playable_tetrominos()

    def place_tetromino(self, tetromino: Tetromino, player: PlayerColor) -> 'TBoard':
        t_board_copy: 'TBoard' = self.copy()
        t_board_copy.place_tetromino_in_place(tetromino, player)

        return t_board_copy
    
    def tetromino_desirability(self, tetromino: Tetromino, player: PlayerColor) -> float:
        return calculate_move_desirability(self.board, tetromino, player, DesirabilityMetric.EMPTY_ADJ_DIFFERENCE)
 
    def __update_playable_tetrominos(self) -> None:
        self.player_playable_tetrominos = self.__find_playable_tetrominos()

    def __find_playable_tetrominos(self) -> dict[PlayerColor, set[Tetromino]]:
        red_tetrominos: set[Tetromino] = set()
        blue_tetrominos: set[Tetromino] = set()

        for coord in all_board_coords():
            blue_adj_token, red_adj_token = self.__has_adj_token(coord, PlayerColor.BLUE), self.__has_adj_token(coord, PlayerColor.RED)

            if coord not in self.board and (blue_adj_token or red_adj_token):
                for tetromino in [tetromino_ for tetromino_ in Tetromino.all_tetrominos_at(coord) if self.__can_place_tetromino(tetromino_)]:
                    if tetromino not in red_tetrominos and red_adj_token:
                        red_tetrominos.add(tetromino)
                    if tetromino not in blue_tetrominos and blue_adj_token:
                        blue_tetrominos.add(tetromino)

        return {PlayerColor.RED: red_tetrominos, PlayerColor.BLUE: blue_tetrominos}
    
    def __can_place_tetromino(self, tetromino: Tetromino) -> bool:
        return all(coord not in self.board for coord in tetromino.tokens)
    
    def __has_adj_token(self, coord: Coord, player: PlayerColor) -> bool:
        return any(self.board[_coord] == player for _coord in [coord.up(), coord.down(), coord.right(), coord.left()] if _coord in self.board)
    
    def __remove_rows(self, rows: list[int]) -> None:
        for row_index in rows:
            for coord in row_coords(row_index):
                if coord in self.board:
                    self.player_num_tokens[self.board[coord]] -= 1
                    del self.board[coord]

    def __remove_cols(self, cols: list[int]) -> None:
        for col_index in cols:
            for coord in col_coords(col_index):
                if coord in self.board:
                    self.player_num_tokens[self.board[coord]] -= 1
                    del self.board[coord]
                
    @staticmethod
    def create_board_id(t_board: 'TBoard') -> int:
        compute_board_position = lambda row, col: row * BOARD_N + col
        board_positions: np.ndarray = np.zeros(BOARD_N * BOARD_N)

        for coord, player in t_board.board.items():
            board_positions[compute_board_position(coord.r, coord.c)] = 2 if player == PlayerColor.RED else 1

        return hash(tuple(board_positions))

    def minimax_depth(self, time_remaining: float | None, player: PlayerColor) -> int:
        if time_remaining == None:
            if (len(self.playable_tetrominos(player)) < 10):
                return 3
            elif (len(self.playable_tetrominos(player)) > 40):
                return 1
            else:       
                return 2
        if (time_remaining > 75):
            if (len(self.playable_tetrominos(player)) < 15):
                return 3
            elif (len(self.playable_tetrominos(player)) > 60):
                return 1
            else:       
                return 2
        elif (time_remaining < 10):
            return 1
        else:
            if (len(self.playable_tetrominos(player)) < 10):
                return 3
            elif (len(self.playable_tetrominos(player)) > 40):
                return 1
            else:       
                return 2