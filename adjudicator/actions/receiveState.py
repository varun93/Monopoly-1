from actions.action import Action

class ReceiveState(Action):
	
	# publishes to all agents
	def publish(self):
		self.agentsYetToRespond = self.state.getLivePlayers()
		currentPlayerId = self.state.getCurrentPlayerId()
		self.publishAction(currentPlayerId,"BROADCAST_IN")
	
	def subscribe(self,*args):
		agentId = None
		if len(args)>0:
			agentId = args[0]
		
		print("Agent "+str(agentId)+" accessed the subscribe of ReceiveState.")
		
		if agentId and self.canAccessSubscribe(agentId) and self.validSubs>=len(self.state.getLivePlayers()):
			nextAction = getattr(self.context, self.nextAction)
			
			nextAction.setContext(self.context)
			nextAction.publish()