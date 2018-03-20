# Gregory Baker
# Cameron Tran
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import numpy as np
import random
import copy
from pattern import pat3set
import sys
import generate_moves as Gm
class GoBoardUtil2(GoBoardUtil):
    """ 
        extends GoBoardUtil to override playgame
    """
    @staticmethod
    def playGame(board, color, **kwargs):
        """
            modified to use custom policy
        """
        komi = kwargs.pop('komi', 0)
        limit = kwargs.pop('limit', 1000)
        random_simulation = kwargs.pop('random_simulation',True)
        use_pattern = kwargs.pop('use_pattern',True)
        check_selfatari = kwargs.pop('check_selfatari',True)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        for _ in range(limit):
            if random_simulation:
                move = GoBoardUtil.generate_random_move(board,color,True)
            else:
                #this uses custom move policy for simulation now
                moves, _ = Gm.generate_moves(board, use_pattern, check_selfatari)
                move = GoBoardUtil.filter_moves_and_generate(board, moves, check_selfatari)
            isLegalMove = board.move(move,color)
            assert isLegalMove
            if board.end_of_game():
                break
            color = GoBoardUtil.opponent(color)
        winner,_ = board.score(komi)  
        return winner