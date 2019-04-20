from actions.action import Action
from config import log
from state import Phase
from utils import check_valid_cash

class AuctionProperty(Action):
	
	def publish(self):
		#auction variables
		currentPlayerId = self.state.getCurrentPlayerId()
		self.auctionWinner = currentPlayerId
		self.winningBid = 1
		self.livePlayers = self.state.getLivePlayers()
		self.agentsYetToRespond = list(self.livePlayers)
		
		log("auction","Agent "+str(currentPlayerId)+" has decided to auction the property "+str(self.state.getPhasePayload()))
		self.publishAction(currentPlayerId,"AUCTION_IN")
	
	def subscribe(self,*args):
		agentId = None
		bid = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			bid = args[1]
		
		if self.canAccessSubscribe(agentId):
			bid = check_valid_cash(bid)
			playerCash = self.state.getCash(agentId)
			
			#Only if the player has enough money should his bid be considered valid
			if bid > self.winningBid and playerCash >= bid:
				self.auctionWinner = agentId
				self.winningBid = bid
			
			#self.validSubs is updated in self.canAccessSubscribe
			if self.validSubs >= len(self.livePlayers):
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
				self.context.receiveState.nextAction = "endTurn"
				
				self.context.receiveState.setContext(self.context)
				self.context.receiveState.publish()
		else:
			print("Agent "+str(agentId)+" was not supposed to respond to auctionProperty here.")
