from action import Action
from ..config import log
from ..utils import typecast

class BuyProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		self.context.publish("com.game{}.agent{}.buy"
				.format(self.context.gameId,currentPlayerId),
				self.state.toJson())
	
	def subscribe(self,response):
		response = self.typecast(response, bool, False)
		if not response:
			self.state.setPhase(Phase.AUCTION)
			self.context.auctionProperty.setContext(self.context)
			self.context.auctionProperty.publish()
		else:
			self.context.buyProperty.setContext(self.context)
			self.context.buyProperty.publish()
