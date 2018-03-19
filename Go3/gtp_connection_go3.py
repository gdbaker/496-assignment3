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
		policy_moves, type_of_move = self.generate_moves()
		if len(policy_moves) == 0:
			self.respond("Pass")
		else:
			response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
			self.respond(response)


	def generate_moves(self):
		"""
			generate a list of policy moves on board for board.current_player.
			calls function from util folder for fallback
		"""
		if self.go_engine.use_pattern:
			if self.board.last_move is not None:

				# checks if atari capture possible
				single_liberty = []
				liberty_point = self.board._single_liberty(self.board.last_move, GoBoardUtil.opponent(self.board.current_player))

				if liberty_point is not None and self.board.check_legal(liberty_point, self.board.current_player):
					single_liberty.append(liberty_point)

					#checks for selfatari
					single_liberty = GoBoardUtil.filter_moves(self.board, single_liberty, self.go_engine.check_selfatari)

					if len(single_liberty) > 0:
						return single_liberty, "AtariCapture"


				#checks for atari defense
				defense_points = self.try_to_defend()
				if len(defense_points) > 0:
					return defense_points, "AtariDefense"



		policy_moves, type_of_move = GoBoardUtil.generate_all_policy_moves(self.board, self.go_engine.use_pattern, self.go_engine.check_selfatari)
		return policy_moves, type_of_move


	def try_to_defend(self):
		neighbours = self.board._neighbors(self.board.last_move)
		plays = []
		for point in neighbours:
			if self.board.get_color(point) == self.board.current_player:
				liberty_point = self.board._single_liberty(point, self.board.current_player)

				if liberty_point is not None:
					# point is block of current player and is in atari
					plays.extend(self.try_runaway(point))
		return plays



	def try_runaway(self, runner):
		works = []
		neighbours = self.board._neighbors(runner)
		for point in neighbours:
			if self.board.get_color(point) == EMPTY and self.board.check_legal(point, self.board.current_player):
				tempBoard = self.board.copy()
				tempBoard.move(point, tempBoard.current_player)
				if tempBoard._liberty(point, self.board.current_player) > 1:
					works.append(point)

		return works


