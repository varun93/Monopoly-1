class ReceiveState(Action):
	
	def publish(self):
		self.context.session.publish("com.game{}.agent{}.receivestate"
			.format(self.context.gameId,self.context.agentId),
			self.state.toJson())
	
	def subscribe(self,response):
		#TODO: Error checking
		
		moduleName,className = self.nextAction.rsplit(".",1)
		classEntity = getattr(importlib.import_module(moduleName), className)
		
		#classEntity represents the class of the action to be invoked next
		action = classEntity(self.context)