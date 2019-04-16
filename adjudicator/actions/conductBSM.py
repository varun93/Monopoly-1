from actions.action import Action
from utils import crange,typecast
from constants import board
from config import log

class ConductBSM(Action):
	
	def publish(self):
		self.agentsYetToRespond = list(self.state.getLivePlayers())
		currentPlayerIndex = self.state.getCurrentPlayerIndex()
		for i in crange(currentPlayerIndex,currentPlayerIndex-1,self.TOTAL_NO_OF_PLAYERS):
				playerId = self.PLAY_ORDER[i]
				if not self.state.hasPlayerLost(playerId):
					self.publishAction(playerId,"BSM_IN")
		
		self.bsmActions = []
		
	def subscribe(self,*args):
		"""
		Stopping conditions for BSM:
		1. If during a given turn no player gave a valid BSM, BSM ends.
		2. A player can only make MAX_BSM_REQUESTS number of requests in a given BSM.
		"""
		agentId = None
		bsmAction = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			bsmAction = args[1]
		
		if self.canAccessSubscribe(agentId):
			#doing no processing here as not all agents have responded yet.
			#want to make this critical section as small as possible.
			self.bsmActions.append( (agentId,bsmAction) )
			
			if self.validSubs>=len(self.state.getLivePlayers()):
				#if all the bsm requests have been received
				actionCount = 0
				mortgageRequests = []
				buyingHousesRequests = []
				buyingHotelsRequests = []
				sellingRequests = []
				for agentId,action in self.bsmActions:
					actionType = self.checkActionType(action) #Some basic validation like syntax,type checking and value range.
					if actionType=="M":
						mortgageRequests.append((agentId,action[1]))
						actionCount+=1
					elif actionType=="BHS":
						if self.state.isBuyingHousesSequenceValid(agentId,action[1]) and hasBuyingCapability(agentId,action[1]):
							buyingHousesRequests.append((agentId,action[1]))
							log("bsm","Player "+str(agentId)+" wants to buy houses.")
							log("bsm",str(action[1]))
							actionCount+=1
					elif actionType=="BHT":
						if self.state.isBuyingHotelSequenceValid(agentId,action[1]):
							buyingHotelsRequests.append((agentId,action[1]))
							log("bsm","Player "+str(agentId)+" wants to buy hotels.")
							log("bsm",str(action[1]))
							actionCount+=1
					elif actionType=="S":
						if self.state.isSellingSequenceValid(agentId,action[1]):
							sellingRequests.append((agentId,action[1]))
							log("bsm","Player "+str(agentId)+" wants to sell houses/hotels.")
							log("bsm",str(action[1]))
							actionCount+=1
					
				"""All agents have responded or have timed out"""
				if actionCount == 0 or self.BSMCount>=10:
					#end bsm and go to the next action
					nextAction = getattr(self.context, self.nextAction)
					nextAction.setContext(self.context)
					nextAction.publish()
				else:
					currentPlayerIndex = self.state.getCurrentPlayerIndex()
					numPlayers = len(self.PLAY_ORDER)
					def sortKey(request):
						return (self.state.getPlayerIndex(request[0])-currentPlayerIndex)%numPlayers
					
					mortgageRequests = sorted(mortgageRequests,key=sortKey)
					buyingHousesRequests = sorted(buyingHousesRequests,key=sortKey)
					buyingHotelsRequests = sorted(buyingHotelsRequests,key=sortKey)
					sellingRequests = sorted(sellingRequests,key=sortKey)
					
					"""Selling Requests"""
					"""First the requests which don't need extra houses or hotels"""
					finishedSellingRequests = []
					for playerId,request in sellingRequests:
						housesNeeded,hotelsNeeded = self.state.evaluateSellingSequence(request)
						if housesNeeded<=0 and hotelsNeeded<=0:
							"""
							Processing this request increases the no of free houses/hotels.
							In other words, this request doesn't clash with any other request. 
							All the other selling requests and buying requests should be processed
							after this to satisfy the maximum number of requests possible.
							"""
							self.handleSell(playerId, request)
							finishedSellingRequests.append(playerId)
					sellingRequests = [entry for entry in sellingRequests if entry[0] not in finishedSellingRequests]
					
					"""Calculate houses needed for Buying Houses Requests"""
					housesRemaining = self.state.getHousesRemaining()
					housesNeededForBHS = 0
					for _,request in buyingHousesRequests:
						housesNeededForBHS += self.state.evaluateBuyingHousesSequence(request)
					housesRemaining -= housesNeededForBHS
					
					"""If there are houses left over, process the remaining selling requests"""
					for playerId,request in sellingRequests:
						housesNeeded,hotelsNeeded = self.state.evaluateSellingSequence(request)
						if housesNeeded<=housesRemaining:
							self.handleSell(playerId, request)
							housesRemaining-=housesNeeded
						else: break
					
					"""Mortgage/Unmortgage requests"""
					for playerId,mortgageRequest in mortgageRequests:
						self.handleMortgage(playerId,mortgageRequest)
					
					isThereAnAuctionInBSM = False
					
					"""Buying Hotels Requests"""
					hotelsRemaining = self.state.getHotelsRemaining()
					hotelsForBHT = 0
					for _,request in buyingHotelsRequests:
						hotelsForBHT += len(request)
					if hotelsRemaining-hotelsForBHT>=0:
						for playerId,request in buyingHotelsRequests:
							self.state.buyHotelSequence(playerId,request)
					else:
						#TODO: AUCTION FOR HOTELS
						#All the hotel requests are in: buyingHotelsRequests
						isThereAnAuctionInBSM = True
						print("auction in BSM")
						self.auctionInBSM(buyingHotelsRequests,"hotels")
					
					"""Buying Houses Requests"""
					housesRemaining = self.state.getHousesRemaining()
					if housesRemaining-housesNeededForBHS>=0:
						for playerId,request in buyingHousesRequests:
							self.handleBuyHouses(playerId,request)
					else:
						#TODO: AUCTION FOR HOUSES
						#All the hotel requests are in: buyingHousesRequests
						isThereAnAuctionInBSM = True
						print("auction in BSM")
						self.auctionInBSM(buyingHousesRequests)
					
					if not isThereAnAuctionInBSM or isThereAnAuctionInBSM: #TODO
						self.BSMCount+=1
						self.setContext(self.context)
						self.publish()
				
	
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
			space = board[propertyId]
			for monopolyPropertyId in space["monopoly_group_elements"]:
				if self.state.getNumberOfHouses(propertyId)>0:
					return False
			
			mortagePrice = int(board[propertyId]['price']/2)
			playerCash += mortagePrice
			log("bsm","Agent "+str(playerId)+" wants to mortgage "+str(propertyId))
			
		for propertyId in unmortgageRequests:
			unmortgagePrice = int(board[propertyId]['price']/2)   

			if propertyId in self.mortgagedDuringTrade:
				self.mortgagedDuringTrade.remove(propertyId)
			else:
				unmortgagePrice = int(unmortgagePrice*1.1)

			if playerCash >= unmortgagePrice:
				playerCash -= unmortgagePrice 
			else:
				return False
			
			log("bsm","Agent "+str(playerId)+" wants to unmortgage "+str(propertyId))
		
		for propertyId in properties:
			self.state.setPropertyMortgaged(propertyId,not self.state.isPropertyMortgaged(propertyId))
		self.state.setCash(playerId,playerCash)
		
	# [(1,4,2),(2,6,1),(3,8,1),(4,9,1)]
	# Triple of playerId, propertyId, numberOfConstructions
	def auctionInBSM(self,buyingDecisions,auctionEntity = "houses"):
		"""
		Bunch of small utilities
		""" 
		def updateBuyingDecisions(buyingDecisions,auctionWinner,propertySite):

			def mapper(triple):
				(playerId,propertyId,constructions) = triple
				if playerId == auctionWinner and propertyId == propertySite:
					return (playerId,propertyId,constructions - 1)
							
				return (playerId,propertyId,constructions)

			buyingDecisions = list(map(mapper, buyingDecisions))
			return list(filter(lambda triple :  triple[2] > 0,buyingDecisions)) 

		def updateWinnerCash(auctionWinner, bidValue):
			auctionWinnerCurrentCash = self.state.getCash(auctionWinner)
			self.state.setCash(auctionWinner,auctionWinnerCurrentCash - bidValue)

		def updateWinnerProperty(auctionedProperty):
			currentConstructions = 4
			if auctionEntity == "houses":
				currentConstructions = self.state.getNumberOfHouses(auctionedProperty)
			
			self.state.setNumberOfHouses(auctionedProperty, currentConstructions + 1)
		
		def getConstructionsRemaining():
			if auctionEntity == "houses":
				return self.state.getHousesRemaining()
			
			return self.state.getHotelsRemaining()

		def transformBuyingDecisions():
			# not doing any checks; to check if the the list is valid 
			def mapper(buyingDecision):
				if auctionEntity == "houses":
					return (buyingDecision[0],buyingDecision[1][0],buyingDecision[1][1])
				return (buyingDecision[0], buyingDecision[1][0],1)

			return list(map(mapper,buyingDecisions))

		"""
		End of Utilities;
		Start of auction logic 
		"""
		pass
