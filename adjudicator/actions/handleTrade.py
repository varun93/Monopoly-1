from actions.action import Action
from utils import crange,typecast,check_valid_cash
from constants import board
from config import log

class HandleTrade(Action):
	
	def publish(self):
		self.agentsYetToRespond = list(self.state.getLivePlayers())
		self.tradeActions = []
		currentPlayerIndex = self.state.getCurrentPlayerIndex()
		for i in crange(currentPlayerIndex,currentPlayerIndex-1,self.TOTAL_NO_OF_PLAYERS):
			playerId = self.PLAY_ORDER[i]
			if not self.state.hasPlayerLost(playerId):
				self.publishAction(playerId,"TRADE_IN")
		
	def subscribe(self,*args):
		"""
		Stopping conditions for Trade:
		1. If during a given turn, no player gave a valid Trade, Trade ends.
		2. A player can only make MAX_TRADE_REQUESTS number of requests in a given Trade Phase.
		"""
		agentId = None
		tradeAction = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			tradeAction = args[1]
		
		if self.canAccessSubscribe(agentId):
			self.tradeActions.append( (agentId,tradeAction) )
			
			if self.validSubs>=len(self.state.getLivePlayers()):
				#if all the trade requests have been received
				actionCount = 0
				validTradeRequests = {}
				for agentId in self.state.getLivePlayers():
					validTradeRequests[agentId] = []
				
				for agentId,action in self.tradeActions:
					if not isinstance(action, list) and not isinstance(action, tuple):
						continue
					if len(action) != 5:
						continue
					otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = action
					if self.validateTradeAction(agentId,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest):
						validTradeRequests[otherAgentId].append((agentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest))
						actionCount+=1

				"""All agents have responded or have timed out"""
				if actionCount == 0:
					#end trade and start the post Trade BSM phase
					self.publishBSM(self.context.conductBSM.nextAction)
				else:
					self.context.tradeResponse.validTradeRequests = validTradeRequests
					self.context.tradeResponse.setContext(self.context)
					self.context.tradeResponse.publish()
	
	def publishBSM(self,nextAction):
		self.context.conductBSM.previousAction = "handleTrade"
		self.context.conductBSM.nextAction = nextAction
		self.context.conductBSM.BSMCount = 0
		self.context.conductBSM.canAgentDoBSM = {}
		for agentId in self.PLAY_ORDER:
			if self.state.hasPlayerLost(agentId):
				self.context.conductBSM.canAgentDoBSM[agentId] = False
			else:
				self.context.conductBSM.canAgentDoBSM[agentId] = True
		self.context.conductBSM.setContext(self.context)
		self.context.conductBSM.publish()
	
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
