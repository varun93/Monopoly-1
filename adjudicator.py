from config import log
import dice
import constants
from cards import Cards
import copy
import timeout_decorator
import json
import numpy as np
from state import State,Phase,Reason

class NumpyEncoder(json.JSONEncoder):
	""" Special json encoder for numpy types """
	def default(self, obj):
		if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
			np.int16, np.int32, np.int64, np.uint8,
			np.uint16, np.uint32, np.uint64, np.bool_)):
			return int(obj)
		elif isinstance(obj, (np.float_, np.float16, np.float32, 
			np.float64)):
			return float(obj)
		elif isinstance(obj,(np.ndarray,)): #### This is the fix
			return obj.tolist()


		return json.JSONEncoder.default(self, obj)

# make sure the state is not mutated
class Adjudicator:
	
	def __init__(self,socket=None):
		
		num_properties = len(constants.space_to_property_map) + 2
		self.socket = socket
		
		self.DiceClass = dice.Dice
		
		"""
		PROPERTY INDICES OF THE STATE VARIABLE
		"""
		self.PLAYER_TURN_INDEX = 0
		self.PROPERTY_STATUS_INDEX = 1
		self.PLAYER_POSITION_INDEX = 2
		self.PLAYER_CASH_INDEX = 3
		self.PLAYER_BANKRUPTCY_STATUS_INDEX = 4
		self.PHASE_NUMBER_INDEX = 5
		self.PHASE_PAYLOAD_INDEX = 6
		self.DEBT_INDEX = 7
		
		self.CHANCE_GET_OUT_OF_JAIL_FREE = 40
		self.COMMUNITY_GET_OUT_OF_JAIL_FREE = 41
		
		self.BOARD_SIZE = 40
		self.PASSING_GO_MONEY = 200
		
		self.MAX_HOUSES = 32
		self.MAX_HOTELS = 12
		
		self.JUST_VISTING = 10
		self.OWNED_BY_BANK = -1
		
		self.dice = None
		
		"""
		CONFIGURATION SETTINGS
		"""
		self.TOTAL_NO_OF_TURNS = 100
		self.INITIAL_CASH = 1500
		
	def notifyUI(self):
		if self.socket is not None:
			# print(self.stateHistory)
			send = json.dumps(self.stateHistory, cls=NumpyEncoder)
			self.socket.emit('game_state_updated', {'state': json.loads(send)} )
	
	"""
	STATE PROPERTIES
	"""
	
	def getPlayerIndex(self,playerId):
		for i in range(self.TOTAL_NO_OF_PLAYERS):
			if self.PLAY_ORDER[i]==playerId:
				return i
		
		return -1
	
	def getPlayer(self,playerIndex):
		return self.agents[playerIndex]
		
	def updateState(self, state, dimensionOneIndex, dimensionTwoIndex, valueToUpdate):
		if dimensionTwoIndex is None:
			state[dimensionOneIndex] = valueToUpdate
		else:
			state[dimensionOneIndex][dimensionTwoIndex] = valueToUpdate
	
	def transformState(self,state):

		transformedState = []

		for element in state:
			if isinstance(element, list):
				transformedState.append(tuple(element))
			elif isinstance(element, dict):
				transformedState.append(tuple([element[1] for element in element.items()]))
			else:
				transformedState.append(element)

		return tuple(transformedState)
	
	"""
	Validation function which checks if the variable `var` can be typecast to datatype `thetype`.
	If there was any exception encountered, return the default value specified
	"""
	def typecast(self,val,thetype,default):
		try:
			if (thetype == bool) and not isinstance(val, thetype):
				return default
			return thetype(val)
		except:
			return default
		
	#Function checks cash passed in through actions by the agent.
	#If cash can't be typecast to int, the cash amount is considered invalid and invalid flows for defaulting would take place.
	def check_valid_cash(self,cash):
		try:
			cash = int(cash)
		except:
			return 0
		if cash < 0:
			return 0
		return cash
	
	def getOtherPlayer(self,currentPlayer):
		if currentPlayer == self.AGENTONE:
			return self.AGENTTWO
		else:
			return self.AGENTONE

	def conductBSM(self):

		"""Returns the type of action. Also checks if the action is valid."""
		def checkActionType(action):
			if not ( isinstance(action, list) or isinstance(action, tuple) ):
				return "N"
			
			type = action[0]
			if (type=="B") or (type=="S"):
				if len(action)<2:
					return "N"
				if not isinstance(action[1], list) and not isinstance(action[1], tuple):
					return "N"
				else:
					for prop in action[1]:
						if not isinstance(prop, list) and not isinstance(prop, tuple):
							return "N"
						else:
							if len(prop)<2:
								return "N"
							if self.typecast(prop[0],int,-1) == -1:
								return "N"
							if self.typecast(prop[1],int,-1) == -1:
								return "N"
			elif type == "M":
				if len(action)<2:
					return "N"
				if not isinstance(action[1], list) and not isinstance(action[1], tuple):
					return "N"
				else:
					for prop in action[1]:
						if self.typecast(prop,int,-1) == -1:
							return "N"
			return type
			
		def hasBuyingCapability(playerIndex,properties):
			playerCash = self.state.getPlayerCash( playerIndex)
			for propertyObject in properties:
				(propertyId,constructions) = propertyObject
				space = constants.board[propertyId]
				playerCash -= space['build_cost']*constructions
				if playerCash < 0:
					break
			return playerCash >= 0
						
		# house can be built only if you own a monopoly of colours 
		# double house can be built only if I have built one house in each colour 
		# order of the tuples to be taken into account
		def handleBuy(agent,properties):
			currentPlayer = agent.id
			
			#Checking if there are properties where houses can't be built
			#Or has invalid number of houses to be built
			invalidProperties = [x for x in properties if (x[1]<0) or (x[1]>5 or constants.board[x[0]]['class']!='Street' )]
			if len(invalidProperties) > 0:
				return False

			if not validBuyingSequence(currentPlayer,properties,1):
				return False

			# determine if the agent actually has the cash to buy all this?
			# only then proceed; important for a future sceanrio
			if not hasBuyingCapability(currentPlayer, properties):
				return False
			
			[remaining_houses,remaining_hotels] = maxHousesHotelsCheck(state,properties,1)
			if remaining_houses==-1 or remaining_hotels==-1:
				log("bstm","Can't buy a house/hotel on "+str(properties)+". Max House limit reached.")
				return False
			
			if not monopolyCheck(state,properties,1):
				return False
			
			playerCash = getPlayerCash(currentPlayer)
			propertyStatusList = [ prop for prop in state[self.PROPERTY_STATUS_INDEX] ]
			
			# ordering of this tuple becomes important  
			for propertyObject in properties:
				(propertyId,constructions) = propertyObject
				space = constants.board[propertyId]
				propertyStatus = propertyStatusList[propertyId]
				currentConstructionsOnProperty = abs(propertyStatus) - 1 

				if constructions and constructions > 0:
					playerCash -= space['build_cost']*constructions
					
					if playerCash >= 0:
						propertyStatus = constructions + currentConstructionsOnProperty + 1
						
						if currentPlayer == self.AGENTTWO:
							propertyStatus *= -1
						
						propertyStatusList[propertyId] = propertyStatus
					else:
						#Should never occur
						return False
			self.updateState(state,self.PROPERTY_STATUS_INDEX,None,propertyStatusList)
			self.updateState(state,self.PLAYER_CASH_INDEX,currentPlayer-1,playerCash)
			return True

		def handleSell(agent,properties):
			playerIndex = self.getPlayerIndex(agent.id)
			
			#Checking if there are properties where houses can't be built
			invalidProperties = [x for x in properties if constants.board[x[0]]['class']!='Street' ]
			if len(invalidProperties) > 0:
				return False
			
			if not validBuyingSequence(playerIndex,properties,-1):
				return False
			
			[remaining_houses,remaining_hotels] = maxHousesHotelsCheck(state,properties,-1)
			if remaining_houses==-1 or remaining_hotels==-1:
				log("bstm","Can't sell a house/hotel on "+str(properties)+". Max House limit reached.")
				return False
			
			if not monopolyCheck(state,properties,-1):
				return False
			
			for (propertyId,constructions) in properties:

				space = constants.board[propertyId]
				playerCash = getPlayerCash( playerIndex)
				propertyStatus = getPropertyStatus(state,propertyId)

				houseCount = abs(propertyStatus) - 1
				
				houseCount -= constructions 
				playerCash += (space['build_cost']*0.5*constructions)

				propertyStatus = houseCount + 1

				if playerIndex == self.AGENTTWO:
					propertyStatus *= -1

				updatePropertyStatus(state,propertyId,propertyStatus)
				self.updateState(state,self.PLAYER_CASH_INDEX,playerIndex-1,playerCash)
			return True

		# If property is mortgaged, player gets back 50% of the price.
		# If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
		# If the player tries to mortgage an invalid property, entire operation fails.
		def handleMortgage(playerIndex,properties):
			playerCash = self.state.getPlayerCash(playerIndex)
			mortgageRequests = []
			unmortgageRequests = []
			
			for propertyId in properties:
				if self.state.getPropertyOwner(propertyId)!=playerIndex:
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
				
				mortagePrice = constants.board[propertyId]['price']/2
				playerCash += mortagePrice
			
			for propertyId in unmortgageRequests:
				unmortgagePrice = constants.board[propertyId]['price']/2	

				if propertyId in self.mortgagedDuringTrade:
					self.mortgagedDuringTrade.remove(propertyId)
				else:
					unmortgagePrice = unmortgagePrice + unmortgagePrice*0.1

				if playerCash >= unmortgagePrice:
					playerCash -= unmortgagePrice 
				else:
					return False
			
			for propertyId in properties:
				self.state.setPropertyMortgaged(propertyId,not self.state.isPropertyMortgaged(propertyId))
			self.state.setCash(playerIndex,playerCash)
		
		"""
		BSMT will be carried out as decision rounds where each player is asked for his BSMT action during that round.
		The flag array 'doneWithBSMT' stores whether each player wants to perform a BSMT action in the current round or not.
		If all the player's don't want to take BSMT actions in a given round, then the BSMT phase ends.
		If a player decides he doesn't want to take any BSMT actions in a given decision round, he can still make BSMT actions in later decision rounds.
		This is done so that he can react to the BSMT decisions made by other players.
		TODO:
		Find a way to ensure that BSMT doesn't go on forever.
		"""
		doneWithBSMT = [False]*(self.TOTAL_NO_OF_PLAYERS)
		
		while False in doneWithBSMT:
			
			#self.updateState(state,self.PHASE_NUMBER_INDEX,None,self.BSTM)
			
			currentPlayerIndex = self.state.getCurrentPlayerIndex()
			mortgageRequests = {}
			buyingRequests = {}
			sellingRequests = {}
			
			while True:
				
				"""Getting the actions for BSMT from all the players"""
				for i in range(self.TOTAL_NO_OF_PLAYERS):
					if not self.state.hasPlayerLost(i):
						action = self.runPlayerOnStateWithTimeout(i)
						actionType = checkActionType(action)
						if actionType=="M":
							mortgageRequests[i]=action
						elif actionType=="B":
							if self.state.isBuyingSequenceValid(i,action[1]) and hasBuyingCapability(i,action[1]):
								buyingRequests[i]=action[1]
						elif actionType=="S":
							if self.state.isSellingSequenceValid(i,action[1]):
								sellingRequests[i]=action[1]
				
				for playerIndex in mortgageRequests.keys():
					handleMortgage(playerIndex,mortgageRequests[playerIndex])
				
				"""Requests where players are selling houses."""
				indices = sellingRequests.keys()
				i=0
				sellingRequestsSize = len(sellingRequests)
				while i<sellingRequestsSize:
					if self.state.doesNoOfHousesIncreaseBySelling(sellingRequests[indices[i]]):
						handleSell(indices[i], sellingRequests[indices[i]])
						del sellingRequests[indices[i]]
						sellingRequestsSize-=1
					else:
						i+=1
				
				"""Rest of the requests could cause contention for houses and hotels"""
				totalHousesNeeded = 0
				totalHotelsNeeded = 0
				for playerIndex in buyingRequests.keys():
					for (_,houses) in buyingRequests[playerIndex]:
						totalHousesNeeded+=houses
				if (totalHousesNeeded<=self.state.getHousesRemaining()):
					pass
				
				"""Requests where players are selling hotels."""
				for playerIndex in sellingRequests.keys():
					pass
			"""
			if agentOneDone and agentTwoDone:
				#Counter against case where we fall on an idle position and do BSTM.
				#The previous phase would be dice roll. But it doesn't make sense to set that back.
				if previousPhaseNumber > self.DICE_ROLL:
					self.updateState(state,self.PHASE_NUMBER_INDEX,None,previousPhaseNumber)
				break
			"""
	
	""" ACTION METHODS """
	"""
	TODO: 
	@Varun: Temporarily moved trade here.
	"""
	def handleTrade(agent,otherAgent,cashOffer,propertiesOffer,cashRequest,propertiesRequest):

		currentPlayer = agent.id
		previousPayload = self.getPhasePayload(currentPlayer)
		
		cashRequest = self.check_valid_cash(cashRequest)
		cashOffer = self.check_valid_cash(cashOffer)
		
		otherPlayer = self.getOtherPlayer(currentPlayer)
		
		s = self.state
		rightOwner, setPropertyStatus, getPropertyStatus, getCash = s.rightOwner, s.setPropertyStatus, s.getPropertyStatus, s.getCash

		currentPlayerCash = getCash(currentPlayer)
		otherPlayerCash = getCash(otherPlayer)

		if cashOffer > currentPlayerCash:
			return False

		if cashRequest > otherPlayerCash:
			return False

		for propertyOffer in propertiesOffer:
			propertyStatus = getPropertyStatus(propertyOffer)
			if not rightOwner(propertyStatus,currentPlayer):
				return False
			if abs(propertyStatus) > 1 and abs(propertyStatus) < 7:
				return False

		# check if the other agent actually cash and properties to offer
		for propertyRequest in propertiesRequest:
			propertyStatus = getPropertyStatus(state,propertyRequest)
			if not rightOwner(propertyStatus,otherPlayer):
				return False
			if abs(propertyStatus) > 1 and abs(propertyStatus) < 7:
				return False
			
		
		phasePayload = [cashOffer,propertiesOffer,cashRequest,propertiesRequest]

		self.updateState(state,self.PHASE_NUMBER_INDEX,None,self.TRADE_OFFER)
		self.updateState(state,self.PHASE_PAYLOAD_INDEX,None,phasePayload)

		tradeResponse = self.runPlayerOnStateWithTimeout(otherAgent,state)
		tradeResponse = self.typecast(tradeResponse, bool, False)
		
		# if the trade was successful update the cash and property status
		if tradeResponse:
			# update the values in the payload index 
			mortgagedProperties = list(filter(lambda propertyId : getPropertyStatus(state,propertyId) in [-7,7], propertiesOffer + propertiesRequest))

			for mortgagedProperty in mortgagedProperties:
				if mortgagedProperty not in mortgagedDuringTrade:
					mortgagedDuringTrade.append(mortgagedProperty)
					space = constants.board[mortgagedProperty]
					propertyPrice = space['price']
					mortgagedPrice = propertyPrice/2
					agentInQuestion = 2

					if getPropertyStatus(state, mortgagedProperty) == -7:
						agentInQuestion = 1
																																					
					agentsCash = getPlayerCash(agentInQuestion)
					agentsCash -= mortgagedPrice*0.1
					self.updateState(state,self.PLAYER_CASH_INDEX,agentInQuestion-1,agentsCash)

			currentPlayerCash = getPlayerCash(currentPlayer)
			otherPlayerCash = getPlayerCash(otherPlayer)

			currentPlayerCash += (cashRequest - cashOffer)
			otherPlayerCash += (cashOffer - cashRequest)
			
			self.updateState(state, self.PLAYER_CASH_INDEX,currentPlayer - 1,currentPlayerCash)
			self.updateState(state, self.PLAYER_CASH_INDEX,otherPlayer - 1,otherPlayerCash)

			for propertyOffer in propertiesOffer:
				propertyStatus = getPropertyStatus(state,propertyOffer) 
				setPropertyStatus(propertyOffer,propertyStatus*-1)

			for propertyRequest in propertiesRequest:
				propertyStatus = getPropertyStatus(state,propertyRequest)
				setPropertyStatus(propertyRequest,propertyStatus*-1)
		
		#Receive State
		#Making the phase number BSTM so that tradeResponse isnt called again
		self.updateState(state,self.PHASE_NUMBER_INDEX,None,self.BSTM)
		phasePayload.insert(0,tradeResponse)
		self.updateState(state,self.PHASE_PAYLOAD_INDEX,None,phasePayload)
		
		self.runPlayerOnStateWithTimeout(agent,state,receiveState=True)
		self.updateState(state,self.PHASE_PAYLOAD_INDEX,None,previousPayload)
		return True
	
	# previousPhaseNumber = state[self.PHASE_NUMBER_INDEX]
	# agentOneDone = False
	# agentTwoDone = False
	# agentOneTradeDone = False
	# agentTwoTradeDone = False

	# mortgageDuringTrade 
	# buy 
	# while there is no response from the one of the players keep querying
	# 

	"""
	Method starts a blind auction.
	First turn in the auction goes to the player who didn't start it. Bidding starts at 1. 
	Any lower bid/ failure to bid in time would result in the property going to the other player. 
	NOTE: This function only accepts UNOWNED PROPERTIES. ENSURE THIS IN THE CALLING FUNCTION.
	"""
	def start_auction(self,auctionedProperty):
		highestBid = 1
		currentParticipant = self.state.getCurrentPlayerId()
		auctionWinner = currentParticipant
		# actually this should be number of live players 
		numberOfPartiesInterested = self.state.getLivePlayers()
		
		while numberOfPartiesInterested > 1:
			
			currentParticipant = (currentParticipant + 1) % N
			currentBid = None

			if self.state.getCash(currentParticipant) > highestBid:
				currentBid = self.agents[currentParticipant].auctionDecision(highestBid)
			
			if currentBid and currentBid > highestBid:
				highestBid = currentBid
				auctionWinner = currentParticipant
			else:
				auctionParticipants[currentParticipant] = False
				numberOfPartiesInterested -= 1 			

		
		auctionWinnerCurrentCash = self.getCurrentPlayerCash(auctionWinner)
		self.state.setCash(auctionWinner,auctionWinnerCurrentCash - highestBid)
		self.state.setPropertyOwner(auctionWinner,auctionedProperty)

		# what is player position?
		# phasePayload = [playerPosition,0]
		# what are these?
		phasePayload = []
		
		self.state.setPhase(auctionWinner,self.PHASE_NUMBER_INDEX)
		self.state.setPhasePayload(auctionWinner,phasePayload)

		return [True,True]
		

	def updateBuyingDecisions(self,buyingDecisions,auctionWinner,propertySite):

		def mapper(triple):
		 	
			(playerId,propertyId,constructions) = triple
			
			if playerId == auctionWinner and propertyId == propertySite:
				return (playerId,propertyId,constructions - 1)
						
			return (playerId,propertyId,constructions)

		buyingDecisions = list(map(mapper, buyingDecisions))
		return list(filter(lambda triple :  triple[2] > 0,buyingDecisions)) 


	# [(1,4,2),(2,6,1),(3,8,1),(4,9,1)]
	# Triple of playerId, propertyId, numberOfConstructions
	def auctionInBSM(self, buyingDecisions):

		maxHouses = self.state.getHousesRemaining() 

		while maxHouses:

			highestBid = min(list(map(lambda triple: self.state.getConstructionValue(triple[1]),buyingDecisions))) 
			interestedParticipants = set(map(lambda triple : triple[0], buyingDecisions))
			participantsCount = len(interestedParticipants) 
			#initializing
			currentParticipant = interestedParticipants[0]
			auctionWinner = currentParticipant
			propertySite = buyingDecisions[0][1]
			
			while participantsCount > 1:
				
				currentBid = None
				propertyId = None

				if self.getCurrentPlayerCash(currentParticipant) > highestBid:
					# Assuming a auction decison API
					(currentBid,propertyId) = self.state.agents[currentParticipant].auctionDecision(highestBid)
			
				if currentBid and currentBid > highestBid:
					highestBid = currentBid
					propertySite = propertyId
					auctionWinner = currentParticipant
				else:
					participantsCount -= 1

				currentParticipant = (currentParticipant + 1) % N

			buyingDecisions = self.updateBuyingDecisions(buyingDecisions,auctionWinner,propertySite)
			maxHouses -= 1
			# update the buyingDecisions  
			auctionWinnerCurrentCash = self.getCurrentPlayerCash(auctionWinner)
			self.state.setCash(auctionWinner,auctionWinnerCurrentCash - highestBid)
			self.state.setPropertyStatus(auctionedProperty,auctionWinner,1)

	
	"""
	(Q: Will there need to be a BSTM if the player receives money?)
	Phase Properties:
	Is the property owned?
	If unowned, there are 3 sequential sub-phases: BSTM,Buying,Auction. Which one are you in?
	If owned, 2 sub-phases: BSTM,rent. Note: BSTM here for opponent must be applied after the turn.
	If cards, draw top card,do effect, return it to bottom of the deck.
	If Go To Jail, send to jail. Immediately end the turn.
	If currently in Jail, 3 ways to get out.
	"""

	"""
	Incoming action format:
	("R",) : represents rolling to get out
    ("P",) : represents paying $50 to get out (BSMT should follow)
    ("C", propertyNumber) : represents using a get out of jail card, 
    but in case someone has both, needs to specify which one they are using. 
    In general, should always specify the number (either 28 or 29)
	Return values are 2 boolean values:
	1. Whether the player is out of jail.
	2. Whether there was a dice throw while handling jail state.
	"""
	def handle_in_jail_state(self,action):
		currentPlayerIndex = self.state.getCurrentPlayerIndex()
		
		if action=="R" or action=="P":
			action = (action,)
		
		if (isinstance(action, tuple) or isinstance(action, list)) and len(action)>0:
			if action[0] == 'P':
				"""
				Should there be a BSMT here?
				Assuming player has the money
				"""
				playerCash = self.state.getCash(currentPlayerIndex)
				#This could cause Bankruptcy. Would cause playerCash to go below 0.
				self.state.setCash(currentPlayerIndex,playerCash-50)
				self.state.setPosition(currentPlayerIndex,self.JUST_VISTING)
				
				self.state.resetJailCounter(currentPlayerIndex)
				return [True,False]
			
			elif action[0] == 'C':
				#Check if the player has the mentioned property card.
				if (len(action)>1) & (action[1] in [self.CHANCE_GET_OUT_OF_JAIL_FREE,self.COMMUNITY_GET_OUT_OF_JAIL_FREE]):
					
					if self.state.getPropertyOwner(currentPlayerIndex)==action[1]:
						if action[1] == self.COMMUNITY_GET_OUT_OF_JAIL_FREE:
							self.chest.deck.append(constants.communityChestCards[4])
						elif action[1] == self.CHANCE_GET_OUT_OF_JAIL_FREE:
							self.chance.deck.append(constants.chanceCards[7])
						
						self.state.setPropertyOwner(currentPlayerIndex,0)
						self.state.setPosition(currentPlayerIndex,self.JUST_VISTING)
						self.state.resetJailCounter(currentPlayerIndex)
						return [True,False]
		
		"""If both the above method fail for some reason, we default to dice roll."""
		diceThrow = None
		if (self.diceThrows is not None) and len(self.diceThrows)>0:
			diceThrow = self.diceThrows.pop(0)
		self.dice.roll(dice=diceThrow)
		if self.dice.double:
			#Player can go out
			#Need to ensure that there is no second turn for the player in this turn.
			self.dice.double = False
			self.state.setPosition(currentPlayerIndex,self.JUST_VISTING)
			self.state.resetJailCounter(currentPlayerIndex)
			return [True,True]
		
		self.state.incrementJailCounter(currentPlayerIndex)
		if self.state.getJailCounter(currentPlayerIndex)==3:
			playerCash = self.state.getCash(currentPlayerIndex)
			#The player has to pay $50 and get out. 
			#This is added as debt so that the player has the opportunity to resolve it.
			self.state.addDebtToBank(currentPlayerIndex,50)
			self.state.setPosition(currentPlayerIndex,self.JUST_VISTING)
			self.state.resetJailCounter(currentPlayerIndex)

			log("jail","Agent "+str(currentPlayerIndex)+" has been in jail for 3 turns. Forcing him to pay $50 to get out.")
			return [True,True]
		return [False,True]
	
	"""
	Returns 2 booleans 
	First is True if not in jail or no longer in jail
	Second is True if dice has already been thrown for the current turn while determining if the player should be let out or remain in jail
	"""
	def handle_jail(self,player):
		currentPlayerIndex = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayerIndex)
		if playerPosition != -1:
			return [True,False]
		
		#InJail
		self.state.setPhase(Phase.JAIL)
		self.state.setPhasePayload(None)
		action = self.runPlayerOnStateWithTimeout(player)
		result = self.handle_in_jail_state(state,action)
		
		phasePayload = [result[0]]
		self.state.setPhasePayload(phasePayload)
		
		#JUSTIFICATION
		#The player needs to know if he is still in jail or not.
		self.broadcastState(state)
		
		return result
	
	def send_player_to_jail(self):
		#Disable double
		self.dice.double = False
		
		currentPlayer = self.state.getCurrentPlayerIndex()
		log("jail","Agent "+str(currentPlayer)+" has been sent to jail")
		self.state.setPosition(currentPlayerIndex,self.JUST_VISTING)
		self.state.setPhase(Phase.JAIL)
		self.state.setPhasePayload(None)
	
	"""
	Dice Roll Function
	1. Checks if player is currently in Jail and handles separately if that is the case.
	2. else, rolls the dice, checks for all the dice events.
	3. Then moves the player to new position and finds out what the effect of the position is.
	"""
	def dice_roll(self,diceThrown):
		
		currentPlayer = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayer)
		playerCash = self.state.getCash(currentPlayer)
		
		if not diceThrown:
			diceThrow = None
			if (self.diceThrows is not None) and len(self.diceThrows)>0:
				diceThrow = self.diceThrows.pop(0)
			self.dice.roll(dice=diceThrow)
			
		"""
		We need to call agent.receiveState and pass on the dice roll for the turn.
		There could be a couple of scenarios:
		1. Player rolls non-doubles
		2. Player rolls doubles.
		3. Player rolls doubles while in Jail.
		4. Player rolls non-doubles while in Jail.
		5. Player rolls doubles for 3 third time in a row in a single turn.
		"""
		
		if self.dice.double_counter == 3:
			self.send_player_to_jail()
			return False
			#End current player's turn here
			#Should there be a GoToJail state to let the player know?
		else:
			#Update player position
			playerPosition += (self.dice.die_1 + self.dice.die_2)
			
			#Passing Go
			if playerPosition>=self.BOARD_SIZE:
				playerPosition = playerPosition % self.BOARD_SIZE
				playerCash += self.PASSING_GO_MONEY
			
			self.state.setCash(currentPlayerIndex,playerCash)
			self.state.setPosition(currentPlayerIndex,playerPosition)
			return True
	
	def isProperty(self,position):
		return (constants.board[position]['class'] == 'Street') or (constants.board[position]['class'] == 'Railroad') or (constants.board[position]['class'] == 'Utility')
	
	"""
	Performed after dice is rolled and the player is moved to a new position.
	Determines the effect of the position and action required from the player.
	"""		
	def determine_position_effect(self):
		currentPlayer = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayer)
		playerCash = self.state.getCash(currentPlayer)
		
		isProperty = self.isProperty(playerPosition)
		
		debt = state[self.DEBT_INDEX]
		
		if isProperty:
			output = self.handle_property()
			if 'phase' in output:
				self.state.setPhase(output['phase'])
			if 'phase_properties' in output:
				self.state.setPhasePayload(output['phase_properties'])
			if 'debt' in output:
				self.state.setDebtToPlayer(currentPlayer,output['debt'][0],output['debt'][1])
			
			if output['phase']==Phase.BUYING:
				action = self.runPlayerOnStateWithTimeout(currentPlayer)
				action = self.typecast(action, bool, False)
				if not action:
					self.state.setPhase(Phase.AUCTION)
			
		elif constants.board[playerPosition]['class'] == 'Chance':
			#Chance
			card = self.chance.draw_card()
			
			log("cards","Chance card \""+str(card['content'])+"\" has been drawn")
			
			#ReceiveState
			phasePayload = [card['id']]
			self.state.setPhase(Phase.CHANCE_CARD)
			self.state.setPhasePayload(phasePayload)
			
			self.broadcastState(state)
			self.handle_cards_pre_turn(state,card,'Chance')
			
		elif constants.board[playerPosition]['class'] == 'Chest':
			#Community
			card = self.chest.draw_card()
			
			log("cards","Community Chest card \""+str(card['content'])+"\" has been drawn")
			
			#ReceiveState
			phasePayload = [card['id']]
			self.state.setPhase(Phase.COMMUNITY_CHEST_CARD)
			self.state.setPhasePayload(phasePayload)

			self.broadcastState(state)
			self.handle_cards_pre_turn(state,card,'Chest')
		   
		elif constants.board[playerPosition]['class'] == 'Tax':
			#Tax
			cash = constants.board[playerPosition]['tax']
			self.state.setPhase(Phase.PAYMENT)
			self.state.setPhasePayload(None)
			self.state.addDebtToBank(currentPlayer,cash)
		
		elif constants.board[playerPosition]['class'] == 'GoToJail':
			self.send_player_to_jail()
		
		elif constants.board[playerPosition]['class'] == 'Idle':
			#Represents Go,Jail(Visiting),Free Parking
			pass

	"""
	Given that the current space is a property, determine what is to be done here.
	This method can only be called for the current player during any given turn.
	Hence only returns a 2 size tuple for debt.
	"""
	def handle_property(self):
		currentPlayer = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayer)
		playerCash = self.state.getCash(currentPlayer)
		
		owner = self.state.getPropertyOwner(playerPosition)
		output = {}
		if owner == self.OWNED_BY_BANK:
			#Unowned
			output['phase'] = Phase.BUYING
			output['phase_properties'] = playerPosition
		elif owner!=currentPlayer:
			
			monopolies = constants.board[playerPosition]['monopoly_group_elements']
			counter = 1
			for monopoly in monopolies:
				monopolyPropOwner = self.state.getPropertyOwner(playerPosition)
				if monopolyPropOwner==owner:
					counter += 1
			
			if (constants.board[playerPosition]['class'] == 'Street'):
				rent = constants.board[playerPosition]['rent']
				if (counter==len(monopolies)+1):
					rent = rent * 2
				
				houseCount = self.state.getNumberOfHouses(propertyId)
				
				if houseCount==1:
					rent = constants.board[playerPosition]['rent_house_1']
				elif houseCount==2:
					rent = constants.board[playerPosition]['rent_house_2']
				elif houseCount==3:
					rent = constants.board[playerPosition]['rent_house_3']
				elif houseCount==4:
					rent = constants.board[playerPosition]['rent_house_4']
				elif houseCount==5:
					rent = constants.board[playerPosition]['rent_hotel']	
				
			elif (constants.board[playerPosition]['class'] == 'Railroad'):
				rent = 25
				if counter == 2:
					rent = 50
				if counter == 3:
					rent = 100
				if counter == 4:
					rent = 200
			elif (constants.board[playerPosition]['class'] == 'Utility'):
				if (counter==len(monopolies)+1):
					rent = 10
				rent = rent * (self.dice.die_1 + self.dice.die_2)
			
			output['phase'] = Phase.PAYMENT
			output['phase_properties'] = playerPosition
			output['debt'] = (owner,rent)
		else:
			#When the property is owned by us
			pass
		
		return output

	"""Method handles various events for Chance and Community cards"""
	def handle_cards_pre_turn(self,state,card,deck):
		currentPlayer = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayer)
		playerCash = self.state.getCash(currentPlayer)
		phaseNumber = self.state.getPhase(currentPlayer)
		updateState = False
		
		phasePayload = None
		
		if card['type'] == 1:
			#-ve represents you need to pay
			if card['money']<0:
				phaseNumber = Phase.PAYMENT
				self.state.addDebtToBank(currentPlayer,abs(card['money']))
			else:
				playerCash += abs(card['money'])

		elif card['type'] == 2:
			#-ve represents you need to pay
			phaseNumber = self.PAYMENT
			if card['money']<0:
				debtAmount = abs(card['money'])
				for i in range(self.TOTAL_NO_OF_PLAYERS):
					if i!=currentPlayer and not self.state.hasPlayerLost(i):
						self.state.setDebtToPlayer(currentPlayer,i,debtAmount)
			else:
				debtAmount = abs(card['money'])
				for i in range(self.TOTAL_NO_OF_PLAYERS):
					if i!=currentPlayer and not self.state.hasPlayerLost(i):
						self.state.setDebtToPlayer(i,currentPlayer,debtAmount)
			
		elif card['type'] == 3:
			if card['position'] == -1:
				#sending the player to jail
				playerPosition = -1
				self.send_player_to_jail()
			else:
				if (card['position'] - 1) < playerPosition:
					#Passes Go
					playerCash += self.PASSING_GO_MONEY
				playerPosition = card['position'] - 1
				updateState = True
				
		elif card['type'] == 4:
			"""Get out of Jail free"""
			if deck == 'Chest':
				propertyValue = self.COMMUNITY_GET_OUT_OF_JAIL_FREE
			else:
				propertyValue = self.CHANCE_GET_OUT_OF_JAIL_FREE
			
			self.state.setPropertyOwner(currentPlayer,propertyValue)
		
		elif card['type'] == 5:
			n_houses = 0
			n_hotels = 0
			for propertyId in range(self.BOARD_SIZE):
				if (self.state.getPropertyOwner(propertyId)==currentPlayer):
					houseCount = self.state.getNumberOfHouses(propertyId)
					if houseCount<5:
						n_houses+=houseCount
					elif houseCount==5:
						n_hotels+=1

			debtAmount = abs(card['money'])*n_houses + abs(card['money2'])*n_hotels
			if debtAmount > 0:
				phaseNumber = Phase.PAYMENT
				self.state.addDebtToBank(currentPlayer,debtAmount)
		
		elif card['type'] == 6:
			#Advance to nearest railroad. Pay 2x amount if owned
			railroads = [i for i in range(self.BOARD_SIZE) if constants.board[i]['class']=='Railroad']
			if (playerPosition < 5) or (playerPosition>=35):
				if (playerPosition>=35):
					#Passes Go
					playerCash += self.PASSING_GO_MONEY
				playerPosition = 5
			elif (playerPosition < 15) and (playerPosition>=5):
				playerPosition = 15
			elif (playerPosition < 25) and (playerPosition>=15):
				playerPosition = 25
			elif (playerPosition < 35) and (playerPosition>=25):
				playerPosition = 35
			
			self.state.setPosition(currentPlayerIndex,playerPosition)
			output = self.handle_property()
			if 'phase' in output:
				phaseNumber = output['phase']
			if 'phase_properties' in output:
				phasePayload = output['phase_properties']
			if 'debt' in output:
				#We need to double rent if the player landed on opponent's property.
				self.state.setDebtToPlayer(currentPlayer,output['debt'][0],output['debt'][1]*2)
		
		elif card['type'] == 7:
			#Advance to nearest utility. Pay 10x dice roll if owned
			utilities = [i for i in range(self.BOARD_SIZE) if constants.board[i]['class']=='Utility']
			if (playerPosition < 12) or (playerPosition>=28):
				if (playerPosition>=28):
					#Passes Go
					playerCash += self.PASSING_GO_MONEY
				playerPosition = 12
			elif (playerPosition < 28) and (playerPosition>=12):
				playerPosition = 28
			
			owner = self.state.getPropertyOwner(playerPosition)
			if owner == self.OWNED_BY_BANK:
				#Unowned
				phaseNumber = Phase.BUYING
				phasePayload = playerPosition
			elif owner!=currentPlayer:
				#Check if owned by opponent
				diceThrow = None
				if (self.diceThrows is not None) and len(self.diceThrows)>0:
					diceThrow = self.diceThrows.pop(0)
				self.dice.roll(ignore=True,dice=diceThrow)
				
				phaseNumber = Phase.PAYMENT
				self.state.setDebtToPlayer(currentPlayer,owner,10 * (self.dice.die_1 + self.dice.die_2))
		
		elif card['type'] == 8:
			#Go back 3 spaces
			playerPosition -= 3 
			updateState = True
		else:
			logger.info('Invalid card type {type}...'.format(type=card['type']))
		
		self.state.setPosition(currentPlayer,playerPosition)
		self.state.setCash(currentPlayer,playerCash)
		self.state.setPhase(phaseNumber)
		self.state.setPhasePayload(phasePayload)
		
		if phaseNumber==Phase.BUYING:
				action = self.runPlayerOnStateWithTimeout(currentPlayer)
				action = self.typecast(action, bool, False)
				if not action:
					self.state.setPhase(Phase.AUCTION)
		
		# make further calls
		if updateState:
			self.determine_position_effect()
	
	"""
	Handle the action response from the Agent for buying an unowned property
	Only called for the currentPlayer during his turn.
	"""	
	def handle_buy_property(self,state):
		currentPlayer = self.state.getCurrentPlayerIndex()
		playerPosition = self.state.getPosition(currentPlayer)
		playerCash = self.state.getCash(currentPlayer)
		
		if playerCash>=constants.board[playerPosition]['price']:
			self.state.setPropertyOwner(currentPlayer,playerPosition)
			log('buy',"Agent "+str(currentPlayer+1)+" has bought "+constants.board[playerPosition]['name'])
			#Clearing the payload as the buying has been completed
			self.state.setPhasePayload(None)
			return True
		
		#This would indicate going to Auction
		return False
	
	"""
	Handling payments the player has to make to the bank/opponent
	Could be invoked for either player during any given turn.
	Returns 2 boolean list - True if the player was able to pay off his debt
	"""
	def handle_payment(self):
		for playerIndex in range(self.TOTAL_NO_OF_PLAYERS):
			if not self.state.hasPlayerLost(playerIndex):
				self.state.clearDebt(playerIndex)
	
	"""Function calls the relevant method of the Agent"""
	def turn_effect(self):
		currentPlayer = self.state.getCurrentPlayerIndex()
		phase = self.state.getPhase(currentPlayer)
		if phase == Phase.BUYING:
			self.handle_buy_property()
		elif phase == Phase.AUCTION:
			#Auction
			#@Varun: TODO
			self.start_auction(state)
			actionOpponent = self.runPlayerOnStateWithTimeout(opponent,state)
			actionCurrentPlayer = self.runPlayerOnStateWithTimeout(currentPlayer,state)
			return self.handle_auction(state,actionOpponent,actionCurrentPlayer)
		elif phase == self.PAYMENT:
			self.handle_payment()
	
	"""
	TODO:
	On final winner calculation, following are considered:
	Player's cash,
	Property value as on the title card,
	House and Hotel purchase value,
	Mortgaged properties at half price.
	"""
	def final_winning_condition(self,state):
		agentOneCash = state[self.PLAYER_CASH_INDEX][0]
		agentTwoCash = state[self.PLAYER_CASH_INDEX][1]
		agentOnePropertyWorth = 0
		agentTwoPropertyWorth = 0
		
		for i in constants.property_to_space_map:
			#In 0 to 39 board position range
			propertyValue =  state[self.PROPERTY_STATUS_INDEX][i]
			propertyPosition = constants.board[ constants.property_to_space_map[ i ] ]
			
			if propertyValue in range(-6,0):
				agentTwoPropertyWorth += (propertyPosition['price'] + ( (abs(propertyValue)-1)*propertyPosition['build_cost'] ) )
			elif propertyValue == -7:
				agentTwoPropertyWorth += (propertyPosition['price']/2)
			elif propertyValue in range(1,7):
				agentOnePropertyWorth += (propertyPosition['price'] + ( (propertyValue-1)*propertyPosition['build_cost'] ) )
			elif propertyValue == 7:
				agentOnePropertyWorth += (propertyPosition['price']/2)
		
		if state[self.PROPERTY_STATUS_INDEX][28] == -1:
			agentTwoPropertyWorth += 50
		elif state[self.PROPERTY_STATUS_INDEX][28] == 1:
			agentOnePropertyWorth += 50
		
		if state[self.PROPERTY_STATUS_INDEX][29] == -1:
			agentTwoPropertyWorth += 50
		elif state[self.PROPERTY_STATUS_INDEX][29] == 1:
			agentOnePropertyWorth += 50
		
		log("win_condition","AgentOne Cash: "+str(agentOneCash))
		log("win_condition","AgentOne Property Value: "+str(agentOnePropertyWorth))
		log("win_condition","AgentTwo Cash: "+str(agentTwoCash))
		log("win_condition","AgentTwo Property Value: "+str(agentTwoPropertyWorth))
		
		if ( (agentOneCash+agentOnePropertyWorth) > (agentTwoCash+agentTwoPropertyWorth) ):
			return 1
		elif ( (agentOneCash+agentOnePropertyWorth) < (agentTwoCash+agentTwoPropertyWorth) ):
			return 2
		else:
			#Tie
			return 0
	
	def initialize_debug_state(self,diceThrows,chanceCards,communityCards):
		if isinstance(diceThrows, list) and len(diceThrows)>0:
			self.diceThrows = diceThrows
		else:
			self.diceThrows = diceThrows
			
		if isinstance(chanceCards, list) and len(chanceCards)>0:
			self.chance.reinit(constants.chanceCards,chanceCards)
		
		if isinstance(communityCards, list) and len(communityCards)>0:
			self.chest.reinit(constants.communityChestCards,communityCards)
			
	def broadcastState(self):
		for playerIndex in range(self.TOTAL_NO_OF_PLAYERS):
			self.runPlayerOnStateWithTimeout(playerIndex,receiveState=True)
	
	"""
	Function to be called to start the game.
	Expects agents to be in the order of play.
	"""
	def runGame(self,agents,diceThrows=None,chanceCards=None,communityCards=None):
		
		self.stateHistory = []
		self.mortgagedDuringTrade = []

		self.chest = Cards(constants.communityChestCards)
		self.chance = Cards(constants.chanceCards)
		
		#Stores the list of agents which are competing in the current game in the order of play.
		self.agents = agents
		self.PLAY_ORDER = [ agent.id for agent in self.agents] #Stores the id's of all the players in the order of play
		self.TOTAL_NO_OF_PLAYERS = len(self.agents)
		
		self.state =  State([agent.id for agent in agents])
		
		#Setting an initial state. Used during testing.
		#if isinstance(state,list) and len(state)==6:
		#	self.state = state
		
		self.initialize_debug_state(diceThrows,chanceCards,communityCards)
		
		while (self.state.turn < self.TOTAL_NO_OF_TURNS) and ( (self.diceThrows is None) or (len(self.diceThrows)>0) ):
			
			log("turn","Turn "+str(self.state.turn)+" start")
			
			playerId = self.state.getCurrentPlayerIndex()
			player = self.getPlayer(playerId)
			
			if self.state.hasPlayerLost(playerId):
				self.state.updateTurn()
				continue
			
			self.state.setPhasePayload(None)
			
			self.dice.reset()
			
			log("state","State at the start of the turn:")
			log("state",self.state)
			
			while ( (self.diceThrows is None) or (len(self.diceThrows)>0) ):
				
				[outOfJail,diceThrown] = self.handle_jail(player)
				if self.state.hasPlayerLost(playerId):
					self.state.updateTurn()
					continue
				
				if outOfJail:
					"""rolls dice, moves the player and determines what happens on the space he has fallen on."""
					notInJail = self.dice_roll(diceThrown)
					if self.state.hasPlayerLost(playerId):
						self.state.updateTurn()
						continue
					
					if notInJail:
						self.determine_position_effect()
						if self.state.hasPlayerLost(playerId):
							self.state.updateTurn()
							continue
						
						log("state","State after moving the player and updating state with effect of the position:")
						log("state",self.state)
						
						"""BSTM"""
						self.conductBSTM()
						if self.state.hasPlayerLost(playerId):
							self.state.updateTurn()
							continue
						
						"""State now contain info about the position the player landed on"""
						"""Performing the actual effect of the current position"""
						result = self.turn_effect()
						if self.state.hasPlayerLost(playerId):
							self.state.updateTurn()
							continue
				
				log("state","State at the end of the turn:")
				log("state",self.state)
				
				if (not self.dice.double):
					break
				else:
					log("dice","Rolled Doubles. Play again.")
			
			log("turn","Turn "+str(self.state.turn)+" end")
			
			"""Update the turn counter"""
			self.state.updateTurn()
			
			if winner is not None:
				break
		
		#Storing the state_history to log file
		f = open("state_history.log", "w")
		for history in self.stateHistory:
			f.write(str(history)+",\n")
		
		"""Determine the winner"""
		if winner==None:
			reason = "Greater Assets"
			winner = self.final_winning_condition(self.state)
		
		if winner == 1:
			log("win","AgentOne won the Game.")
		elif winner == 2:
			log("win","AgentTwo won the Game.")
		else:
			log("win","It's a Tie!")

		#add to the state history
		#Clearing the payload as it might contain some internal info used by the adjudicator
		self.state.setPhasePayload(None)
		finalState = list(self.state)
		finalState.pop(7)
		finalState.append(reason)
		finalState = self.transformState(finalState)
		log("win","Final State:")
		log("win",finalState)
		self.notifyUI()
		return [winner,finalState]
	
	"""
	This function is called whenever adjudicator needs to communicate with the agent
	The function to called on the agent is determined by reading the state.
	All threading and signal based logic must go in here
	"""
	@timeout_decorator.timeout(3, timeout_exception=TimeoutError)
	def runPlayerOnStateWithTimeout(self, playerIndex,receiveState=False):
		try:
			return self.runPlayerOnState(playerIndex,receiveState)
		except TimeoutError:
			print("Agent Timed Out")
			"""Change the return value here to ensure agent loose"""
			self.state.markPlayerLost(playerIndex,Reason.TIMEOUT)
			return None

	def runPlayerOnState(self,playerIndex,receiveState=False):
		player = self.getPlayer(playerIndex)
		action = None
		current_phase = self.state.getPhase(playerIndex)
		stateToBeSent = self.state

		if receiveState:
			action = player.receiveState(stateToBeSent)
		elif current_phase == Phase.BSTM:
			action = player.getBSMTDecision(stateToBeSent)
		elif current_phase == Phase.TRADE_OFFER:
			action = player.respondTrade(stateToBeSent)
		elif current_phase == Phase.BUYING:
			action = player.buyProperty(stateToBeSent)
		elif current_phase == Phase.AUCTION:
			action = player.auctionProperty(stateToBeSent)
		elif current_phase == Phase.PAYMENT:
			pass
		elif current_phase == Phase.JAIL:
			action = player.jailDecision(stateToBeSent)
		
		return action

# for testing purposes only
#adjudicator = Adjudicator()
#adjudicator.runGame(agentOne, agentTwo)