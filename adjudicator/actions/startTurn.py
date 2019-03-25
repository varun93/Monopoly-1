from action import Action
from ..config import log

class StartTurn(Action):
	
	def publish(self):
		#turnNo starts from -1
		if (self.state.getTurn()+1 >= self.TOTAL_NO_OF_TURNS):
			#skip this turn.
			pass
		self.state.updateTurn()
		
		playerId = self.state.getCurrentPlayerId()
		if self.state.hasPlayerLost(playerId):
			#skip this turn.
			pass
		
		self.dice.reset()
			
		log("turn","Turn "+str(self.state.getTurn())+" start")
		
		#no communication with the user here.
		self.subscribe()
	
	def subscribe(self):
		self.context.jailDecision.setContext(self.context)
		self.context.jailDecision.publish()