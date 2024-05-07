from ..referee.game.coord import Coord
from ..referee.game.player import PlayerColor
from ..referee.game.constants import BOARD_N, MAX_TURNS
from .tetromino import Tetromino
from .t_board_counter import TBoardCounter
from .utils import row_coords, col_coords

class TBoard:
    def __init__(
        self,
        board: dict[Coord, PlayerColor] = {},
        turn_count: int = 0,
        player_playable_tetrominos: dict[PlayerColor, set[Tetromino]] = {},
        t_board_counter: TBoardCounter = TBoardCounter()
    ):
        self.board: dict[Coord, PlayerColor] = board
        self.turn_count: int = turn_count
        self.player_playable_tetrominos: dict[PlayerColor, set[Tetromino]] = player_playable_tetrominos
        self.t_board_counter: TBoardCounter = t_board_counter

    def playable_tetrominos(self, player: PlayerColor ) -> list[Tetromino]:
        return list(self.player_playable_tetrominos[player])
    
    def max_turn_reached(self) -> bool:
        return self.turn_count == MAX_TURNS

    def player_score(self, player: PlayerColor) -> float:
        if self.max_turn_reached():
            player_tokens: int = self.t_board_counter.num_tokens(player)
            opponent_tokens: int = self.t_board_counter.num_tokens(player.opponent())
            return float('inf') if player_tokens > opponent_tokens else float('-inf') if player_tokens < opponent_tokens else 0

        return len(self.player_playable_tetrominos[player]) - len(self.player_playable_tetrominos[player.opponent()])
    
    def copy(self) -> 'TBoard':
        return TBoard(self.board.copy(), self.turn_count, self.player_playable_tetrominos.copy(), self.t_board_counter.copy())

    def __place_tetromino(self, tetromino: Tetromino, player: PlayerColor) -> None:
        for token in tetromino.tokens:
            if token in self.board:
                raise Exception("Placing token in occupied coordinate")
            
            self.board[token] = player

        self.turn_count += 1

        removed_rows, removed_cols = self.t_board_counter.place_tetromino(tetromino, player)
        self.__remove_rows(removed_rows)
        self.__remove_cols(removed_cols)

        self.__update_playable_tetrominos()

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
                        if tetromino not in tetrominos and self.__can_place_tetromino(tetromino, player):
                            tetrominos.add(tetromino)

        return tetrominos
    
    def __can_place_tetromino(self, tetromino: Tetromino, player: PlayerColor,) -> bool:
        return all(coord not in self.board for coord in tetromino.tokens)
    
    def __has_adj_token(self, coord: Coord, player: PlayerColor) -> bool:
        return any(self.board[_coord] == player for _coord in [coord.up(), coord.down(), coord.right(), coord.left()])
    
    def __remove_rows(self, rows: list[int]) -> None:
        for row in rows:
            for coord in row_coords(row):
                if coord not in self.board:
                    raise Exception("Removing non-existent token")
                del self.board[coord]

    def __remove_cols(self, cols: list[int]) -> None:
        for col in cols:
            for coord in col_coords(col):
                if coord not in self.board:
                    raise Exception("Removing non-existent token")
                del self.board[coord]
    
    @staticmethod 
    def place_tetromino(t_board: 'TBoard', tetromino: Tetromino) -> 'TBoard':
        t_board_copy: 'TBoard' = t_board.copy()
        t_board_copy.__place_tetromino(tetromino)

        return t_board_copy
