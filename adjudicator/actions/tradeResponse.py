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
		
