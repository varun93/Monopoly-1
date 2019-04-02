from actions.action import Action
from config import log
from dice import Dice
from cards import Cards
from state import State
from constants import communityChestCards,chanceCards

class StartGame(Action):
	
	def publish(self):
		self.context.dice = Dice()
		self.context.chest = Cards(communityChestCards)
		self.context.chance = Cards(chanceCards)
		self.context.state =  State(self.PLAY_ORDER)
		self.context.mortgagedDuringTrade = []
		self.context.winner = None
			
		log("game","Game #"+str(self.context.gamesCompleted)+" started.")
		
		#Allow the agent to initialize state for a new game
		self.publishAction(currentPlayerId,"START_GAME_IN")
	
	def subscribe(self):
		self.context.startTurn.setContext(self.context)
		self.context.startTurn.publish()