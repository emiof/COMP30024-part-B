from referee.game.pieces import _TEMPLATES
from referee.game.coord import Coord
from referee.game.actions import Action

class Tetromino:
    """
    Class that represents a tetromino in the game, comprising four tokens, each defined using an instance of Coord. 
    """
    def __init__(self, c1: Coord, c2: Coord, c3: Coord, c4: Coord):
        self.tokens: list[Coord] = [c1, c2, c3, c4]

    def create_action(self) -> Action:
        return Action(*self.tokens)
    
    def __hash__(self) -> int:
        return hash(tuple(self.tokens))
    
    def __eq__(self, other: 'Tetromino') -> bool:
        return self.tokens == other.tokens
    
    @staticmethod
    def all_tetrominos_at(at: Coord) -> list['Tetromino']:
        return [Tetromino(*[at + coord for coord in piece]) for piece in _TEMPLATES.values()]
    
    @staticmethod
    def tetromino_from_action(action: Action) -> 'Tetromino':
        return Tetromino(*action.coords)
