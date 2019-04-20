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
			currentPlayerId = self.state.getCurrentPlayerId()
			if self.dice.double and not self.state.hasPlayerLost(currentPlayerId):
				log("dice","Rolled Doubles. Play again.")
				self.context.jailDecision.setContext(self.context)
				self.context.jailDecision.publish()
			else:
				if self.isOption(currentPlayerId,"END_TURN"):
					self.agentsYetToRespond = [currentPlayerId]
					self.publishAction(currentPlayerId,"END_TURN_IN")
				else:
					#no communication with the user here.
					self.context.startTurn.setContext(self.context)
					self.context.startTurn.publish()
	
	def subscribe(self,*args):
		agentId = None
		if len(args)>0:
			agentId = args[0]
		
		if agentId and self.canAccessSubscribe(agentId):
			self.context.startTurn.setContext(self.context)
			self.context.startTurn.publish()
		else:
			print("Agent "+str(agentId)+" was not supposed to respond to endTurn here.")

	"""
	Handling payments the player has to make to the bank/opponent
	Could be invoked for either player during any given turn.
	Returns 2 boolean list - True if the player was able to pay off his debt
	"""
	def handle_payment(self):
		for playerId in self.PLAY_ORDER:
			if not self.state.hasPlayerLost(playerId):
				self.state.clearDebt(playerId)
	