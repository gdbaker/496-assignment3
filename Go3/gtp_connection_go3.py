"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
# modified by
#Gregory Baker
#Cameron Tran
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection

class GtpConnectionGo3(gtp_connection.GtpConnection):

	def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
		"""
		GTP connection of Go1

		Parameters
		----------
		go_engine : GoPlayer
			a program that is capable of playing go by reading GTP commands
		komi : float
			komi used for the current game
		board: GoBoard
			SIZExSIZE array representing the current board state
		"""
		gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
		
		self.commands["policy_moves"] = self.policy_moves_cmd


	def policy_moves_cmd(self, args):
		"""
		Return list of policy moves for the current_player of the board
		"""
		policy_moves, type_of_move = self.generate_all_policy_moves()
		if len(policy_moves) == 0:
			self.respond("Pass")
		else:
			response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
			self.respond(response)


	def generate_all_policy_moves(self):
		"""
			generate a list of policy moves on board for board.current_player.
			Use in UI only. For playing, use generate_move_with_filter
			which is more efficient
		"""
		if self.go_engine.use_pattern:
			if self.board.last_move is not None:

				# checks if atari capture possible
				single_liberty = self.board._single_liberty(self.board.last_move, GoBoardUtil.opponent(self.board.current_player))
				if single_liberty is not None:
					return [single_liberty], "AtariCapture"

			pattern_moves = []
			pattern_moves = GoBoardUtil.generate_pattern_moves(self.board)
			pattern_moves = GoBoardUtil.filter_moves(self.board, pattern_moves, self.go_engine.check_selfatari)
			if len(pattern_moves) > 0:
				print(pattern_moves)
				return pattern_moves, "Pattern"
		return GoBoardUtil.generate_random_moves(self.board,True), "Random"










