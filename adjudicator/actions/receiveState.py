class ReceiveState(Action):
	
	#TODO: publish to all agents
	def publish(self):
		self.context.session.publish("com.game{}.agent{}.receivestate"
			.format(self.context.gameId,self.context.agentId),
			self.state.toJson())
	
	def subscribe(self,agentId):
		#TODO: Error checking
		
		nextAction = getattr(self.context, self.nextAction)
		
		nextAction.setContext(self.context)
		nextAction.publish()