from actions.action import Action

class ConductBSM(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		pass
	
	def subscribe(self,response):
		pass
