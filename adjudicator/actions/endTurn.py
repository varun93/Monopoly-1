from actions.action import Action
from config import log
from constants import board

class EndTurn(Action):
	
	def publish(self):
		log("turn","Turn "+str(self.state.getTurn())+" end")
		self.handle_payment()
		
		lossCount = 0
		for agentId in self.PLAY_ORDER:
			if self.state.hasPlayerLost(agentId): lossCount+=1
		
		if (lossCount>=self.TOTAL_NO_OF_PLAYERS-1) or (self.state.getTurn()+1 >= self.TOTAL_NO_OF_TURNS):
			#Only one player left or last turn is completed. Winner can be decided.
			self.context.endGame.setContext(self.context)
			self.context.endGame.publish()
		else:
			if self.dice.double:
				log("dice","Rolled Doubles. Play again.")
				self.context.jailDecision.setContext(self.context)
				self.context.jailDecision.publish()
			else:
				self.context.startTurn.setContext(self.context)
				self.context.startTurn.publish()
	
	def subscribe(self):
		pass

	"""
	Handling payments the player has to make to the bank/opponent
	Could be invoked for either player during any given turn.
	Returns 2 boolean list - True if the player was able to pay off his debt
	"""
	def handle_payment(self):
		for playerId in self.PLAY_ORDER:
			if not self.state.hasPlayerLost(playerId):
				self.state.clearDebt(playerId)
	