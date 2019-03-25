from action import Action
from ..config import log

class HandlePayment(Action):
	
	def publish(self):
		self.handle_payment()
		self.subscribe()
	
	def subscribe(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		if self.state.hasPlayerLost(currentPlayerId):
			self.context.endTurn.setContext(self.context)
			self.context.endTurn.publish()
		else:
			if self.dice.double:
				log("dice","Rolled Doubles. Play again.")
				self.context.jailDecision.setContext(self.context)
				self.context.jailDecision.publish()
			else:
				self.context.endTurn.setContext(self.context)
				self.context.endTurn.publish()
	
	"""
	Handling payments the player has to make to the bank/opponent
	Could be invoked for either player during any given turn.
	Returns 2 boolean list - True if the player was able to pay off his debt
	"""
	def handle_payment(self):
		for playerId in self.PLAY_ORDER:
			if not self.state.hasPlayerLost(playerId):
				self.state.clearDebt(playerId)
