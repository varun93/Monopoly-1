from actions.action import Action
from utils import typecast
from constants import board
from config import log

class TradeResponse(Action):
	
	def publish(self):
		if isinstance(self.validTradeRequests,dict):
			self.agentsYetToRespond = []
			for agentId,tradeRequests in self.validTradeRequests.items():
				if len(tradeRequests) > 0:
					self.agentsYetToRespond.append(agentId)
			
			self.number_of_requests = len(self.agentsYetToRespond)
			if self.number_of_requests <= 0:
				#end trade and start the post Trade BSM phase
				self.publishBSM(self.context.handleTrade.nextAction)
			
			self.previosPhase = self.state.getPhase()
			self.state.setPhase(Phase.TRADE_RESPONSE)
			self.tradeResponseList = []
			for agentId,tradeRequests in self.validTradeRequests.items():
				if len(tradeRequests) > 0:
					self.state.setPhasePayload(tradeRequests)
					self.publishAction(agentId,"RESPOND_TRADE_IN")
		else:
			#end trade and start the post Trade BSM phase
			self.publishBSM(self.context.handleTrade.nextAction)
		
	def subscribe(self,*args):
		"""
		Stopping conditions for Trade:
		1. If during a given turn, no player gave a valid Trade, Trade ends.
		2. A player can only make MAX_TRADE_REQUESTS number of requests in a given Trade Phase.
		"""
		agentId = None
		tradeResponse = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			tradeResponse = args[1]
		
		if self.canAccessSubscribe(agentId):
			self.tradeResponseList.append( (agentId,tradeResponse) )
			
			if self.validSubs>=self.number_of_requests:
				#if all the trade requests have been received
				for agentId,tradeResponses in self.tradeResponseList:
					for tradeResponse in tradeResponses:
						tradeResponse = typecast(tradeResponse, bool, False)
						if tradeResponse:
							otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = self.validTradeRequests[agentId]
							if self.validateTradeAction(agentId,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest):
								#we do trade request validation here because if a user accepts multiple trades that were
								#presented to him at a time, and if he accepts 2 conflicting trades, the adjudicator should
								#not let both not let both of them through
								self.processTradeSuccess(agentId,self.validTradeRequests[agentId])
				
				self.context.handleTrade.tradeCount+=1
				if self.context.handleTrade.tradeCount>=self.MAX_TRADE_REQUESTS:
					#end trade and start the post Trade BSM phase
					self.publishBSM(self.context.conductBSM.nextAction)
				else:
					#start the next trade
					self.context.handleTrade.setContext(self.context)
					self.context.handleTrade.publish()
	
	def publishBSM(self,nextAction):
		self.context.conductBSM.previousAction = "handleTrade"
		self.context.conductBSM.nextAction = nextAction
		self.context.conductBSM.BSMCount = 0
		self.context.conductBSM.setContext(self.context)
		self.context.conductBSM.publish()
	
	def processTradeSuccess(self,otherAgentId,tradeRequest):
		agentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = tradeRequest
		
		currentPlayerCash =  self.state.getCash(agentId)
		otherPlayerCash = self.state.getCash(otherAgentId)

		currentPlayerCash += (cashRequest - cashOffer)
		otherPlayerCash += (cashOffer - cashRequest)
		
		self.state.setCash(agentId,currentPlayerCash)
		self.state.setCash(otherAgentId,otherPlayerCash)

		for propertyRequest in propertiesRequest:
			self.state.setPropertyOwner(propertyRequest,agentId)
		for propertyOffer in propertiesOffer:
			self.state.setPropertyOwner(propertyOffer,otherAgentId)
				
		#Handle mortgaged properties that were involved in the trade after transferring ownership
		mortgagedProperties = list(filter(lambda propertyId : self.state.isPropertyMortgaged(propertyId), propertiesOffer + propertiesRequest))
		for mortgagedProperty in mortgagedProperties:
			if mortgagedProperty not in self.mortgagedDuringTrade:
				self.mortgagedDuringTrade.append(mortgagedProperty)
				space = board[mortgagedProperty]
				propertyPrice = space['price']
				mortgagedPrice = int(propertyPrice/2)
				agentInQuestion = self.state.getPropertyOwner(mortgagedProperty)

				agentsCash = self.state.getCash(agentInQuestion)
				agentsCash -= int(mortgagedPrice*0.1)
				self.state.setCash(agentInQuestion,agentsCash)
	
	"""
	Property may be Get Out of Jail Free cards (propertyId = 40,41)
	The property being traded and other properties in the same color group
	can't have houses/hotels on them.
	"""
	def validPropertyToTrade(self,playerId, propertyId):
		propertyId = typecast(propertyId,int,-1)
		if propertyId<0 or propertyId>self.BOARD_SIZE+1:
			return False
		if not self.state.rightOwner(playerId,propertyId):
			return False
		if propertyId > self.BOARD_SIZE-1:
			return True
		if board[propertyId]['class']=="Railroad" and board[propertyId]['class']=="Utility":
			return True
		if board[propertyId]['class']!="Street":
			return False
		if self.state.getNumberOfHouses(propertyId) > 0:
			return False
		for monopolyElement in board[propertyId]['monopoly_group_elements']:
			if self.state.getNumberOfHouses(monopolyElement) > 0:
				return False
		return True
	
	"""Checks if a proposed trade is valid"""
	def validateTradeAction(self,agentId,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest):
		
		passed = False
		if otherAgentId == agentId:
			return False
		for playerId in self.state.getLivePlayers():
			if otherAgentId == playerId:
				passed = True
				break
		if not passed:
			return False
		
		cashOffer = check_valid_cash(cashOffer)
		cashRequest = check_valid_cash(cashRequest)
		currentPlayerCash = self.state.getCash(agentId)
		otherPlayerCash = self.state.getCash(otherAgentId)
		if cashOffer > currentPlayerCash:
			return False
		if cashRequest > otherPlayerCash:
			return False
		
		if not isinstance(propertiesOffer, list) and not isinstance(propertiesOffer, tuple):
				return False
		else:
			for propertyId in propertiesOffer:
				if not validPropertyToTrade(agentId, propertyId):
					return False
		
		if not isinstance(propertiesRequest, list) and not isinstance(propertiesRequest, tuple):
				return False
		else:
			for propertyId in propertiesRequest:
				if not validPropertyToTrade(otherAgentId, propertyId):
					return False
		
		return True
		
