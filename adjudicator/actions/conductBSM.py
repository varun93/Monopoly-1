from actions.action import Action
from utils import crange,typecast
from constants import board

class ConductBSM(Action):
	
	def publish(self):
		self.agentsYetToRespond = self.state.getLivePlayers()
		currentPlayerIndex = self.state.getCurrentPlayerIndex()
		for i in crange(currentPlayerIndex,currentPlayerIndex-1,self.TOTAL_NO_OF_PLAYERS):
				playerId = self.PLAY_ORDER[i]
				if not self.state.hasPlayerLost(playerId):
					self.publishAction(currentPlayerId,"BSM_IN")
		
		self.actionCount = 0
		self.mortgageRequests = []
		self.buyingHousesRequests = []
		self.buyingHotelsRequests = []
		self.sellingRequests = []
		
	def subscribe(self,action):
		"""
		Stopping conditions for BSM:
		1. If during a given turn no player gave a valid BSM, BSM ends.
		2. A player can only make MAX_BSM_REQUESTS number of requests in a given BSM.
		"""
		if self.canAccessSubscribe(agentId):
			actionType = self.checkActionType(action) #Some basic validation like syntax,type checking and value range.
			if actionType=="M":
				self.mortgageRequests.append((playerId,action[1]))
				self.actionCount+=1
			elif actionType=="BHS":
				if self.state.isBuyingHousesSequenceValid(playerId,action[1]) and hasBuyingCapability(playerId,action[1]):
					self.buyingHousesRequests.append((playerId,action[1]))
					log("bsm","Player "+str(playerId)+" wants to buy houses.")
					log("bsm",str(action[1]))
					self.actionCount+=1
			elif actionType=="BHT":
				if self.state.isBuyingHotelSequenceValid(playerId,action[1]):
					self.buyingHotelsRequests.append((playerId,action[1]))
					log("bsm","Player "+str(playerId)+" wants to buy hotels.")
					log("bsm",str(action[1]))
					self.actionCount+=1
			elif actionType=="S":
				if self.state.isSellingSequenceValid(playerId,action[1]):
					self.sellingRequests.append((playerId,action[1]))
					log("bsm","Player "+str(playerId)+" wants to sell houses/hotels.")
					log("bsm",str(action[1]))
					self.actionCount+=1
			
			if len(self.agentsYetToRespond)==0:
				if self.actionCount == 0:
					pass
				else:
					pass
	
	"""Returns the type of action. Also checks if the action is valid."""
	def checkActionType(self,action):
		if not ( isinstance(action, list) or isinstance(action, tuple) ) or len(action)<2:
			return "N"
		
		type = action[0]
		if type=="BHS":
			if not ( isinstance(action[1], list) or isinstance(action[1], tuple) ):
				return "N"
			else:
				for prop in action[1]:
					if not ( isinstance(prop, list) or isinstance(prop, tuple) ) or len(prop)<2:
						return "N"
					else:						   
						firstElem = typecast(prop[0],int,-1)
						secondElem = typecast(prop[1],int,-1)
						if firstElem<0 or firstElem>self.BOARD_SIZE-1:
							return "N"
						if secondElem<0 or secondElem>4:
							return "N"
		elif type=="S":
			if not ( isinstance(action[1], list) or isinstance(action[1], tuple) ):
				return "N"
			else:
				for prop in action[1]:
					if not ( isinstance(prop, list) or isinstance(prop, tuple) ) or len(prop)<3:
						return "N"
					else:						   
						firstElem = typecast(prop[0],int,-1)
						secondElem = typecast(prop[1],int,-1)
						thirdElem = typecast(prop[2], bool, False)
						if firstElem<0 or firstElem>self.BOARD_SIZE-1:
							return "N"
						if secondElem<0 or secondElem>4:
							return "N"
		elif type == "M" or type=="BHT":
			if not isinstance(action[1], list) and not isinstance(action[1], tuple):
				return "N"
			else:
				for prop in action[1]:
					firstElem = typecast(prop,int,-1)
					if firstElem<0 or firstElem>self.BOARD_SIZE-1:
						return "N"
		return type
	
	def hasBuyingCapability(self,playerId,properties):
		playerCash = self.state.getCash(playerId)
		for propertyId,constructions in properties:
			space = board[propertyId]
			playerCash -= space['build_cost']*constructions
			if playerCash < 0:
				break
		return playerCash >= 0
					
	# house can be built only if you own a monopoly of colours 
	# double house can be built only if I have built one house in each colour 
	# order of the tuples to be taken into account
	def handleBuyHouses(self,playerId,properties):
		playerCash = self.state.getCash(playerId)
		for propertyId,constructions in properties:
			houseCount = self.state.getNumberOfHouses(propertyId)
			houseCount += constructions
			playerCash -= board[propertyId]['build_cost']*constructions
			self.state.setNumberOfHouses(propertyId,houseCount)
		self.state.setCash(playerId,playerCash)
		return True

	def handleSell(self,playerId,properties):
		playerCash = self.state.getCash(playerId)
		
		for propertyId,constructions,hotel in properties:
			space = board[propertyId]
			if hotel: constructions+=1
			houseCount = self.state.getNumberOfHouses(propertyId)
			houseCount -= constructions
			playerCash += int(space['build_cost']*0.5*constructions)
			self.state.setNumberOfHouses(propertyId,houseCount)
		
		self.state.setCash(playerId,playerCash)
		return True

	# If property is mortgaged, player gets back 50% of the price.
	# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
	# If the player tries to mortgage an invalid property, entire operation fails.
	def handleMortgage(self,playerId,properties):
		playerCash = self.state.getCash(playerId)
		mortgageRequests = []
		unmortgageRequests = []
		
		for propertyId in properties:
			if self.state.getPropertyOwner(propertyId)!=playerId:
				return False
			
			#It could be that the player is getting money to unmortgage a property 
			#by mortgaging other properties. Hence, processing mortgage requests first.
			if self.state.isPropertyMortgaged(propertyId):
				unmortgageRequests.append(propertyId)
			else:
				mortgageRequests.append(propertyId)
		
		for propertyId in mortgageRequests:
			#There should be no houses on a property to be mortgaged or in any other property in the monopoly.
			if self.state.getNumberOfHouses(propertyId)>0:
				return False
			space = constants.board[propertyId]
			for monopolyPropertyId in space["monopoly_group_elements"]:
				if self.state.getNumberOfHouses(propertyId)>0:
					return False
			
			mortagePrice = int(board[propertyId]['price']/2)
			playerCash += mortagePrice
			log("bsm","Player "+str(playerId)+" wants to mortgage.")
			
		for propertyId in unmortgageRequests:
			unmortgagePrice = int(constants.board[propertyId]['price']/2)   

			if propertyId in self.mortgagedDuringTrade:
				self.mortgagedDuringTrade.remove(propertyId)
			else:
				unmortgagePrice = int(unmortgagePrice*1.1)

			if playerCash >= unmortgagePrice:
				playerCash -= unmortgagePrice 
			else:
				return False
			
			log("bsm","Player "+str(playerId)+" wants to unmortgage.")
		
		log("bsm",str(properties))  
		for propertyId in properties:
			self.state.setPropertyMortgaged(propertyId,not self.state.isPropertyMortgaged(propertyId))
		self.state.setCash(playerId,playerCash)
