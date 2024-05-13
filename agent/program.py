# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
from .t_board import TBoard
from .tetromino import Tetromino
from .best_next_move import best_next_move

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """
    #start with empty board class from previous project

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.t_board: TBoard = TBoard()

        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")


    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        if self.t_board.turn_count <= 1:
            return self.t_board.any_playable_tetromino().create_action()

        alpha, beta = float('-inf'), float('inf')
        time_remaining: float = referee['time_remaining']
        space_remaining: float = referee['space_remaining']
        
        minimax_depth = self.t_board.minimax_depth(time_remaining, self._color, max_depth=6, normal_depth=3, min_depth=2)
        _, tetromino = best_next_move(self.t_board, self._color, self._color, alpha, beta, minimax_depth)
        return tetromino.create_action()

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        self.t_board.place_tetromino_in_place(Tetromino.tetromino_from_action(action), color)
        
        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
