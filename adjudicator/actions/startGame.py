from actions.action import Action
from config import log
from dice import Dice
from cards import Cards
from state import State,Property,NUMBER_OF_PROPERTIES
from constants import communityChestCards,chanceCards

class StartGame(Action):
	
	def publish(self):
		self.context.dice = Dice()
		self.context.chest = Cards(communityChestCards)
		self.context.chance = Cards(chanceCards)
		if self.context.INITIAL_STATE == "DEFAULT":
			self.context.state =  State(self.PLAY_ORDER)
		elif self.context.INITIAL_STATE == "TEST_BUY_HOUSES":
			properties = [Property(0,False,False,0,i) for i in range(NUMBER_OF_PROPERTIES)]
			agentOne = self.PLAY_ORDER[0]
			properties[6].owned = True
			properties[6].ownerId = agentOne
			properties[8].owned = True
			properties[8].ownerId = agentOne
			properties[9].owned = True
			properties[9].ownerId = agentOne
			agentTwo = self.PLAY_ORDER[1]
			properties[11].owned = True
			properties[11].ownerId = agentTwo
			properties[13].owned = True
			properties[13].ownerId = agentTwo
			properties[14].owned = True
			properties[14].ownerId = agentTwo
			self.context.state = State(self.PLAY_ORDER,properties)
		self.context.winner = None
			
		log("game","Game #"+str(self.context.gamesCompleted+1)+" started.")
		
		#Allow the agent to initialize state for a new game
		self.agentsYetToRespond = list(self.PLAY_ORDER)
		self.publishAction(None,"START_GAME_IN")
	
	def subscribe(self,*args):
		agentId = None
		if len(args)>0:
			agentId = args[0]
		
		#self.validSubs is updated in self.canAccessSubscribe
		if self.canAccessSubscribe(agentId) and self.validSubs>=len(self.PLAY_ORDER):
			self.context.startTurn.setContext(self.context)
			self.context.startTurn.publish()