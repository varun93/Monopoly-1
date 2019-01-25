import random
from collections import namedtuple

StateTuple = namedtuple("StateTuple", "turn properties positions money bankrupt phase phaseData debt")

INITIAL_CASH = 1500
MAX_HOUSES = 32
MAX_HOTELS = 12
TOTAL_NO_OF_PLAYERS = 4


class State:

	def __init__(self, numberOfPlayers):
		TOTAL_NO_OF_PLAYERS = numberOfPlayers
		
		self.turn = 0
		self.properties = [0]*42
		self.positions = [0]*TOTAL_NO_OF_PLAYERS
		self.money = [INITIAL_CASH]*TOTAL_NO_OF_PLAYERS
		self.bankrupt = [False]*TOTAL_NO_OF_PLAYERS
		self.phase = Phase.BSMT
		self.phaseData = None
		self.debt = [0]*(2*TOTAL_NO_OF_PLAYERS)

	def getHousesRemaining(self):
		houses = MAX_HOUSES
		for prop in self.properties:
			if (prop%TOTAL_NO_OF_PLAYERS > 1) and (prop%TOTAL_NO_OF_PLAYERS <6): houses -= (prop-1)
		return houses

	def getHotelsRemaining(self):
		hotels = MAX_HOTELS
		for prop in self.properties:
			if (prop%TOTAL_NO_OF_PLAYERS == 6): hotels -= 1
		return hotels

	def toTuple(self):
		return StateTuple(self.turn, tuple(self.properties), tuple(self.positions),
						  tuple(self.money), self.phase, self.phaseData, tuple(self.debt))

	def __str__(self):
		return str(self.toTuple())