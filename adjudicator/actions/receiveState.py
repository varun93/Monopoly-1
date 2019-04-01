from actions.action import Action

class ReceiveState(Action):
	
	#TODO: publish to all agents
	def publish(self):
		self.agentsYetToRespond = self.state.getLivePlayers()
		currentPlayerId = self.state.getCurrentPlayerId()
		self.publishAction(currentPlayerId,"BROADCAST_IN")
	
	def subscribe(self,*args):
		#TODO: Error checking and timeout handling
		agentId = None
		if len(args)>0:
			agentId = args[0]
		
		print("Agent "+str(agentId)+" accessed the subscribe of ReceiveState.")
		
		if agentId and self.canAccessSubscribe(agentId):
			nextAction = getattr(self.context, self.nextAction)
			
			nextAction.setContext(self.context)
			nextAction.publish()