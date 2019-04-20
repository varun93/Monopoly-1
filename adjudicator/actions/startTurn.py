from actions.action import Action
from config import log

class StartTurn(Action):
	
	def publish(self):
		#turnNo starts from -1
		if self.state.getTurn()+1 >= self.TOTAL_NO_OF_TURNS:
			#skip this turn.
			self.context.endTurn.setContext(self.context)
			self.context.endTurn.publish()
		self.state.updateTurn()
		
		playerId = self.state.getCurrentPlayerId()
		if self.state.hasPlayerLost(playerId):
			#skip this turn.
			self.context.endTurn.setContext(self.context)
			self.context.endTurn.publish()
		
		self.dice.reset()
			
		log("turn","Turn "+str(self.state.getTurn())+" start")
		
		currentPlayerId = self.state.getCurrentPlayerId()
		if self.isOption(currentPlayerId,"START_TURN"):
			self.agentsYetToRespond = [currentPlayerId]
			self.publishAction(currentPlayerId,"START_TURN_IN")
		else:
			#no communication with the user here.
			self.context.jailDecision.setContext(self.context)
			self.context.jailDecision.publish()
	
	def subscribe(self,*args):
		agentId = None
		if len(args)>0:
			agentId = args[0]
		
		if self.canAccessSubscribe(agentId):
			self.context.jailDecision.setContext(self.context)
			self.context.jailDecision.publish()
		else:
			print("Agent "+str(agentId)+" was not supposed to respond to startTurn here.")
		