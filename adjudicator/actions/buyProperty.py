from action import Action
from ..config import log
from ..utils import typecast

class BuyProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		agent_attributes = self.context.genAgentChannels(currentPlayerId,requiredChannel = "BUY_IN")
		self.context.publish(agent_attributes["BUY_IN"], self.state.toJson())
	
	def subscribe(self,agentId,response):
		response = self.typecast(response, bool, False)
		if not response:
			self.state.setPhase(Phase.AUCTION)
			self.context.auctionProperty.setContext(self.context)
			self.context.auctionProperty.publish()
		else:
			self.context.buyProperty.setContext(self.context)
			self.context.buyProperty.publish()
