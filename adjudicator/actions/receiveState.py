from actions.action import Action

class ReceiveState(Action):
	
	#TODO: publish to all agents
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		agent_attributes = self.context.genAgentChannels(currentPlayerId,requiredChannel = "BROADCAST_IN")
		self.context.publish(agent_attributes["BROADCAST_IN"], self.state.toJson())
	
	def subscribe(self,agentId):
		#TODO: Error checking and timeout ahndling
		
		nextAction = getattr(self.context, self.nextAction)
		
		nextAction.setContext(self.context)
		nextAction.publish()