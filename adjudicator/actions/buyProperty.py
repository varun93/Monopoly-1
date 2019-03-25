from action import Action
from ..config import log
from ..utils import typecast
from ..state import Phase
from ..constants import board

class BuyProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		log("buy","Agent "+str(currentPlayerId)+" has landed on the unowned property "+
		self.state.getPhasePayload())
		agent_attributes = self.context.genAgentChannels(currentPlayerId,requiredChannel = "BUY_IN")
		self.context.publish(agent_attributes["BUY_IN"], self.state.toJson())
	
	def subscribe(self,agentId,response):
		response = typecast(response, bool, False)
		if not response:
			self.state.setPhase(Phase.AUCTION)
			self.context.auctionProperty.setContext(self.context)
			self.context.auctionProperty.publish()
		else:
			if self.handle_buy_property():
				#The property was successfully bought TODO
				self.context.endTurn.setContext(self.context)
				self.context.endTurn.publish()
			else:
				self.context.auctionProperty.setContext(self.context)
				self.context.auctionProperty.publish()
	
	def handle_buy_property(self):
		"""
		Handle the action response from the Agent for buying an unowned property
		Only called for the currentPlayer during his turn.
		"""
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		playerCash = self.state.getCash(currentPlayerId)
		space = board[playerPosition]
		
		if playerCash>=space['price']:
			self.state.setPropertyOwner(playerPosition,currentPlayerId)
			self.state.setCash(currentPlayerId,playerCash-space['price'])
			log('buy',"Agent "+str(currentPlayerId)+" has bought "+space['name'])
			#Clearing the payload as the buying has been completed
			self.state.setPhasePayload(None)
			return True
		
		#This would indicate going to Auction
		return False
