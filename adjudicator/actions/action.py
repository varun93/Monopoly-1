import six
import abc

import constants
from dice import Dice
from state import State
from cards import Cards

@six.add_metaclass(abc.ABCMeta)
class Action:
	
	def __init__(self,staticContext):
		self.BOARD_SIZE = staticContext["BOARD_SIZE"]
		self.CHANCE_GET_OUT_OF_JAIL_FREE = staticContext["CHANCE_GET_OUT_OF_JAIL_FREE"]
		self.COMMUNITY_GET_OUT_OF_JAIL_FREE = staticContext["COMMUNITY_GET_OUT_OF_JAIL_FREE"]
		self.JUST_VISTING = staticContext["JUST_VISTING"]
		self.JAIL = staticContext["JAIL"]
		self.PLAY_ORDER = staticContext["PLAY_ORDER"]
		self.TOTAL_NO_OF_PLAYERS = staticContext["TOTAL_NO_OF_PLAYERS"]
		
		
	
	def setContext(self,context):
		self.context = context
		
		self.PASSING_GO_MONEY = context.PASSING_GO_MONEY
		self.TOTAL_NO_OF_TURNS = context.TOTAL_NO_OF_TURNS
		self.INITIAL_CASH = context.INITIAL_CASH
		
		self.dice = context.dice
		self.chest = context.chest
		self.chance = context.chance
		self.state = context.state
		self.mortgagedDuringTrade = context.mortgagedDuringTrade
		self.winner = context.winner
		

	@abc.abstractmethod
	def publish(self):
		"""
		Publishes an action on the agent's channel.
		"""	
	
	@abc.abstractmethod
	def subscribe(self,*args,**kwargs):
		"""
		Callback invoked by the agent when it is done with an action.
		"""