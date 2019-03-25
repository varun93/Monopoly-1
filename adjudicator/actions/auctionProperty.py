from action import Action

class AuctionProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		self.context.publish("com.game{}.agent{}.auction"
				.format(self.context.gameId,currentPlayerId),
				self.state.toJson())
	
	def subscribe(self,agentId,response):
		pass
