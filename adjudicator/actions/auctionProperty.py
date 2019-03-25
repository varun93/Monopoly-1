from action import Action

class AuctionProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		agent_attributes = self.context.genAgentChannels(currentPlayerId,requiredChannel = "AUCTION_IN")
		self.context.publish(agent_attributes["AUCTION_IN"], self.state.toJson())
	
	def subscribe(self,agentId,response):
		pass
