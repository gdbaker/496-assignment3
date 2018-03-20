# Gregory Baker
# Cameron Tran
# move generation using custom policy

from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import numpy as np

def generate_moves(board, use_pattern, check_selfatari):
	"""
		generate a list of policy moves on board for board.current_player.
		calls function from util folder for fallback
	"""
	if use_pattern:
		if board.last_move is not None:

			# checks if atari capture possible
			single_liberty = []
			liberty_point = board._single_liberty(board.last_move, GoBoardUtil.opponent(board.current_player))

			if liberty_point is not None and board.check_legal(liberty_point, board.current_player):
				single_liberty.append(liberty_point)

				#checks for selfatari
				single_liberty = GoBoardUtil.filter_moves(board, single_liberty, check_selfatari)

				if len(single_liberty) > 0:
					return single_liberty, "AtariCapture"


			#checks for atari defense
			defense_points = try_to_defend(board)
			defense_points = GoBoardUtil.filter_moves(board, defense_points, check_selfatari)
			if len(defense_points) > 0:
				return defense_points, "AtariDefense"

	policy_moves, type_of_move = GoBoardUtil.generate_all_policy_moves(board, use_pattern, check_selfatari)
	return policy_moves, type_of_move


def try_to_defend(board):
	"""
		tries possible ways to defend
	"""
	neighbours = board._neighbors(board.last_move)
	plays = []
	for point in neighbours:
		if board.get_color(point) == board.current_player:
			liberty_point = board._single_liberty(point, board.current_player)

			if liberty_point is not None:
				# point is block of current player and is in atari
				plays.extend(try_runaway(liberty_point, board))
				plays.extend(try_capture(point, board))
	return plays



def try_runaway(point, board):
	"""
		finds possible defense by running away
	"""
	works = []
	if board.get_color(point) == EMPTY and board.check_legal(point, board.current_player):
		tempBoard = board.copy()
		tempBoard.move(point, tempBoard.current_player)

		if tempBoard._liberty(point, board.current_player) > 1:
			works.append(point)

	return works

def try_capture(capPoint, board):
	"""
		finds possible defense by capturing opponent
	"""
	works = []
	opponentBlocks = modified_flood_fill(capPoint, GoBoardUtil.opponent(board.current_player), board)

	for point in opponentBlocks:
		liberty = board._single_liberty(point, GoBoardUtil.opponent(board.current_player))

		if liberty is not None and board.check_legal(liberty, board.current_player):
			works.append(liberty)

	return works

def modified_flood_fill(capPoint, colour, board):
	"""
		modified floodfill from util folder to 
		return the adjacent opponent points
	"""
	fboard = np.array(board.board, copy=True)
	pointstack = [capPoint]
	fboard[capPoint] = FLOODFILL
	opponentBlocks = []
	while pointstack:
		current_point = pointstack.pop()
		neighbors = board._neighbors(current_point)
		for n in neighbors :
			if fboard[n] == board.current_player:
				fboard[n] = FLOODFILL
				pointstack.append(n)
			elif fboard[n] ==  colour:
				fboard[n] = BORDER
				opponentBlocks.append(n)
	return opponentBlocks


