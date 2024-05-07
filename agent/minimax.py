from referee.game import PlayerColor
from referee.game import constants

def minimax(BoardClass board, color: PlayerColor, depth, alpha, beta, bool: maximisingPlayer):
    playableTetronimos = playable_tetronimos(board)
    if (depth == 0 or board.turnCount == MAX_TURNS or len(playableTetronimos) == 0): 
        #reached max depth or terminal state
        return player_score(PlayerColor, board)
    if (maximisingPlayer):
        #returns move with highest player score
        value = float('-inf')
        for move in playableTetronimos:
            boardCopy = board.copy()
            boardCopy._placeTetronimo(move)
            value = max(minimax(boardCopy, PlayerColor, depth - 1, alpha, beta, False))
            if (value > beta):
                break
            alpha = max(value, alpha)
        return value
    else: #minimising player
        value = float('inf')
        for move in playableTetronimos:
            boardCopy = board.copy()
            boardCopy._placeTetronimo(move)
            value = min(minimax(boardCopy, PlayerColor, depth - 1, alpha, beta, True))
            if (value < alpha):
                break
            beta = min(value, beta)
        return value
        
    
