from actions.action import Action
from config import log
from utils import typecast
from state import Phase
from constants import board

class BuyProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		self.agentsYetToRespond = [currentPlayerId]
		
		log("buy","Agent "+str(currentPlayerId)+" has landed on the unowned property "+str(self.state.getPhasePayload()))
		self.publishAction(currentPlayerId,"BUY_IN")
	
	def subscribe(self,*args):
		agentId = None
		response = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			response = args[1]
		
		if agentId and self.canAccessSubscribe(agentId):
			response = typecast(response, bool, False)
			if not response:
				self.state.setPhase(Phase.AUCTION)
				self.context.auctionProperty.setContext(self.context)
				self.context.auctionProperty.publish()
			else:
				if self.handle_buy_property():
					#The property was successfully bought
					self.context.endTurn.setContext(self.context)
					self.context.endTurn.publish()
				else:
					#player didnt have enough cash
					self.state.setPhase(Phase.AUCTION)
					self.context.auctionProperty.setContext(self.context)
					self.context.auctionProperty.publish()
		else:
			print("Agent "+str(agentId)+" was not supposed to respond to buyProperty here.")
	
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
