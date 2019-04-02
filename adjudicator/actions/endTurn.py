from actions.action import Action
from config import log
from constants import board

class EndTurn(Action):
	
	def publish(self):
		log("turn","Turn "+str(self.state.getTurn())+" end")
		self.subscribe()
	
	def subscribe(self):
		lossCount = 0
		for agentId in self.PLAY_ORDER:
			if self.state.hasPlayerLost(agentId): lossCount+=1
		if (lossCount>=self.TOTAL_NO_OF_PLAYERS-1) or (self.state.getTurn()+1 >= self.TOTAL_NO_OF_TURNS):
			#Only one player left or last turn is completed. Winner can be decided.
			self.context.endGame.setContext(self.context)
			self.context.endGame.publish()
			
		else:
			self.context.startTurn.setContext(self.context)
			self.context.startTurn.publish()
	