from actions.action import Action
from config import log
from state import Phase
from utils import check_valid_cash

class AuctionProperty(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		
		#auction variables
		self.auctionWinner = currentPlayerId
		self.winningBid = 1
		self.bidsReceived = 0
		self.livePlayers = self.state.getLivePlayers()
		
		log("auction","Agent "+str(currentPlayerId)+" has decided to auction the property "+str(self.state.getPhasePayload()))
		agent_attributes = self.context.genAgentChannels(currentPlayerId,requiredChannel = "AUCTION_IN")
		self.context.publish(agent_attributes["AUCTION_IN"], self.state.toJson())
	
	def subscribe(self,agentId,bid):
		bid = check_valid_cash(bid)
		playerCash = self.state.getCash(agentId)
		
		#Only if the player has enough money should his bid be considered valid
		if bid > self.winningBid and playerCash >= bid:
			self.auctionWinner = agentId
			self.winningBid = bid
		
		self.bidsReceived+=1
		if self.bidsReceived >= len(self.livePlayers):
			log("auction","Agent "+self.auctionWinner+" won the Auction with a bid of "+str(self.winningBid))
			
			auctionedProperty = self.state.getPhasePayload()
			playerCash = self.state.getCash(self.auctionWinner)
			playerCash -= self.winningBid
			self.state.setCash(self.auctionWinner,playerCash)
			self.state.setPropertyOwner(auctionedProperty,self.auctionWinner)   
			
			#Receive State
			phasePayload = [auctionedProperty,self.auctionWinner,self.winningBid]
			self.state.setPhasePayload(phasePayload)
			self.context.receiveState.previousAction = "auctionProperty"
			self.context.receiveState.nextAction = "endTurn" #TODO
			
			self.context.receiveState.setContext(self.context)
			self.context.receiveState.publish()
