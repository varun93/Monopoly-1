import random
from collections import namedtuple
from constants import board
import json

StateTuple = namedtuple("StateTuple", "turn properties positions money bankrupt phase phaseData debt")

INITIAL_CASH = 1500
MAX_HOUSES = 32
MAX_HOTELS = 12
TOTAL_NO_OF_PLAYERS = 4
NUMBER_OF_PROPERTIES = 42

class Property(dict):
	def __init__(self,houses,hotel,mortgaged,owned,ownerId):
		self.houses = houses #value in range 0-4
		self.hotel = hotel #boolean
		self.mortgaged = mortgaged #boolean
		self.owned = owned #boolean
		self.ownerId = ownerId
		dict.__init__(self, houses=houses,hotel=hotel,mortgaged=mortgaged,owned=owned,ownerId=ownerId) #for json parsing

class Debt(dict):
	def __init__(self,bank,otherPlayers):
		self.bank = bank
		self.otherPlayers = otherPlayers
		dict.__init__(self,bank=bank,otherPlayers=otherPlayers) #for json parsing

class State:
	def __init__(self, playerIds):		
		#List of id's of all the agents in the order in which the game will take place.
		self.players = playerIds
		TOTAL_NO_OF_PLAYERS = len(playerIds)
		
		self.turn = 0
		self.properties = [Property(0,False,False,False,0)]*NUMBER_OF_PROPERTIES
		self.positions = {}
		self.cash = {}
		self.bankrupt = {}
		self.phase = Phase.BSMT
		self.phasePayload = None
		self.debt = {}
		
		self.jailCounter = {}
		self.timeoutTracker = {}
		self.reason_for_loss = {}
		self.turn_of_loss = {}
		for playerId in self.players:
			self.positions[playerId] = 0
			self.cash[playerId] = INITIAL_CASH
			self.bankrupt[playerId] = False
			self.jailCounter[playerId] = 0
			self.timeoutTracker[playerId] = False
			self.reason_for_loss[playerId] = None
			self.turn_of_loss[playerId] = -1
			
			bankDebt = 0
			otherPlayersDebt = {}
			for otherPlayerId in self.players:
				if otherPlayerId!=playerId:
					otherPlayersDebt[otherPlayerId] = 0 #debt to other players
			self.debt[playerId] = Debt(bankDebt,otherPlayersDebt)
	
	"""The index of the player in the players array"""
	"""This represents the order of play for the player"""
	def getCurrentPlayerIndex(self):
		return self.turn % TOTAL_NO_OF_PLAYERS
	
	"""Actual Player Id set inside the agent accessible as agent.id attribute"""
	def getCurrentPlayerId(self):
		return self.players[self.getCurrentPlayerIndex()]
	
	def getPlayerId(self,playerIndex):
		return self.players[playerIndex]
	
	"""TURN"""
	def getTurn(self):
		return self.turn
	
	def updateTurn(self):
		self.turn+=1
	
	"""POSITION"""
	def getPosition(self,playerId):
		self.positions[playerId]
	
	def setPosition(self,playerId,position):
		self.positions[playerId] = position
	
	"""CASH"""
	def getCash(self,playerId):
		self.cash[playerId]
		
	def setCash(self,playerId,cash):
		self.cash[playerId] = cash
	
	"""BANKRUPT"""
	def hasPlayerLost(self,playerId):
		return self.bankrupt[playerId]
	
	def markPlayerLost(self,playerId,reason):
		self.bankrupt[playerId] = True
		self.reason[playerId] = reason
		if reason==Reason.TIMEOUT:
			self.timeoutTracker[playerId]=True
		self.turn_of_loss[playerId] = self.turn
	
	def getTurnOfLoss(self,playerId):
		return self.turn_of_loss[playerId]
	
	"""PHASE"""
	def getPhase(self):
		return self.phase
		
	def setPhase(self,phase):
		self.phase = phase
	
	"""PHASE PAYLOAD"""
	def getPhasePayload(self):
		return self.phasePayload
		
	def setPhasePayload(self,phasePayload):
		self.phasePayload = phasePayload

	"""DEBT"""
	#TODO: FOLLOWING 2 METHODS ARE CURRENTLY NOT USED. ARE THEY NEEDED?
	def getDebtToPlayers(self,playerId):
		totalDebt = 0
		for _,otherPlayerDebt in self.debt[playerId].otherPlayers.items():
			totalDebt+=otherPlayerDebt
		return totalDebt
	
	def getDebtToBank(self,playerId):
		return self.debt[playerId].bank
	
	def setDebtToPlayer(self,playerId,otherPlayerId,amount):
		self.debt[playerId][otherPlayerId] = amount
	
	def addDebtToBank(self,playerId,debt):
		self.debt[playerId].bank += debt
	
	def clearDebt(self,playerId):
		playerCash = self.getCash(playerId)
		for otherPlayerId,debt in self.debt[playerId].otherPlayers.items():
			if playerCash>= debt:
				playerCash-=debt
				self.setCash(otherPlayerId, self.getCash(otherPlayerId)+debt)
				self.debt[playerIndex][otherPlayerId] = 0
			else:
				#Unpaid debt to another player, on rare occasion, there could be debts to multiple players.
				self.markPlayerLost(playerId, Reason.BANKRUPT)
				pass
		debtToBank = self.debt[playerId].bank
		if playerCash>=debtToBank:
			playerCash-=debtToBank
			self.debt[playerId].bank = 0
		else:
			#Unpaid debt to the bank
			self.markPlayerLost(playerId, Reason.BANKRUPT)
			pass
		
	"""JAIL COUNTER"""
	def getJailCounter(self,playerId):
		return self.jailCounter[playerId]
	
	def incrementJailCounter(self,playerId):
		self.jailCounter[playerId]+=1
	
	def resetJailCounter(self,playerId):
		self.jailCounter[playerId]=0
	
	"""PROPERTIES"""
	
	"""OWNERSHIP FUNCTIONS"""
	def isPropertyOwned(self,propertyId):
		return self.properties[propertyId].owned
	
	def setPropertyUnowned(self,propertyId):
		self.properties[propertyId].owned = False
		self.properties[propertyId].houses = 0
		self.properties[propertyId].hotel = False
		self.properties[propertyId].mortgaged = False
		
	def getPropertyOwner(self,propertyId):
		return self.properties[propertyId].ownerId
	
	def setPropertyOwner(self,propertyId,playerId):
		self.properties[propertyId].owned = True
		self.properties[propertyId].ownerId = playerId
		self.properties[propertyId].houses = 0 #If a property changes ownership, it should always have no houses on it.
	
	# logic to be changed
	def rightOwner(self,playerId,propertyId):
		return self.properties[propertyId].owned and self.getPropertyOwner(propertyId) == playerId
	
	"""MORTGAGE FUNCTIONS"""
	def isPropertyMortgaged(self,propertyId):
		return self.properties[propertyId].mortgaged
	
	def setPropertyMortgaged(self,propertyId,mortgaged):
		self.properties[propertyId].mortgaged = mortgaged
	
	"""HOTEL FUNCTIONS"""
	def getHotel(self,propertyId):
		return self.properties[propertyId].hotel
	
	def isBuyingHotelSequenceValid(self,playerId,propertySequence,sequenceType):
		for propertyId in propertySequence:
			currentProperty = self.properties[propertyId]
			if (currentProperty.ownerId!=playerId) or (currentProperty.mortgaged) or (currentProperty.houses<4):
				return False
			if currentProperty.hotel:
				return False
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyProperty = self.properties[monopolyPropertyId]
				if (monopolyProperty.ownerId!=playerId) or (monopolyProperty.mortgaged) or (monopolyProperty.houses<4):
					return False
		return True
	
	def buyHotel(self,propertyId,playerId):
		playerCash = self.getCash(playerId)
		if not self.properties[propertyId].hotel:
			playerCash -= board[propertyId]["build_cost"] #don't deduct cash if there was already a hotel here
		self.properties[propertyId].hotel = True
		self.setCash(playerId, playerCash)
		
	def sellHotel(self,propertyId,playerId):
		playerCash = self.getCash(playerId)
		if self.properties[propertyId].hotel:
			playerCash += board[propertyId]["build_cost"]
		self.properties[propertyId].hotel = False
		self.setCash(playerId, playerCash)
	
	"""HOUSES FUNCTIONS"""
	def getNumberOfHouses(self,propertyId):
		return self.properties[propertyId].houses
	
	def setNumberOfHouses(self,propertyId,count):
		self.properties[propertyId].houses = count
	
	"""
	This function checks the following:
	Checks if the properties are streets
	That the player owns all the properties in the monopoly and that they are all unmortgaged.
	That the end result of the buying operation results in houses being built evenly.
	If even one fault is found, the entire operation is invalidated,
	"""
	def isBuyingHousesSequenceValid(self, playerId,propertySequence):
		propertiesCopy = list(self.properties)
		for propertyId,housesCount in propertySequence:
			if board[propertyId]['class']!="Street":
				return False
			
			currentProperty = propertiesCopy[propertyId]
			if (currentProperty.ownerId!=playerId) or (currentProperty.mortgaged) or (currentProperty.hotel):
				return False
			
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyProperty = propertiesCopy[monopolyPropertyId]
				if (monopolyProperty.ownerId!=playerId) or (monopolyProperty.mortgaged) or (monopolyProperty.hotel):
					return False
			
			newHousesCount = currentProperty.houses+housesCount
			if (newHousesCount>4) or (newHousesCount<0):
				return False
			
			propertiesCopy[propertyId].houses+=housesCount
		
		for propertyId,_ in propertySequence:
			houses = propertiesCopy[propertyId].houses
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyHouses = propertiesCopy[monopolyPropertyId].houses
				if abs(monopolyHouses-houses)>1:
					return False
		return True
		
	def isSellingSequenceValid(self,playerId,propertySequence):
		propertiesCopy = list(self.properties)
		for propertyId,housesCount,hotel in propertySequence:
			if board[propertyId]['class']!="Street":
				return False
			
			currentProperty = propertiesCopy[propertyId]
			if (currentProperty.ownerId!=playerId) or (currentProperty.mortgaged) or (hotel and not currentProperty.hotel) or (not hotel and currentProperty.hotel and housesCount!=0):
				return False
			
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyProperty = propertiesCopy[monopolyPropertyId]
				if (monopolyProperty.ownerId!=playerId) or (monopolyProperty.mortgaged) or (hotel and monopolyProperty.houses<4):
					return False
			
			newHousesCount = currentProperty.houses-housesCount
			if (newHousesCount>4) or (newHousesCount<0):
				return False
			
			if hotel:
				propertiesCopy[propertyId].hotel=False
			propertiesCopy[propertyId].houses+=housesCount
		
		for propertyId,_ in propertySequence:
			houses = propertiesCopy[propertyId].houses
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyHouses = propertiesCopy[monopolyPropertyId].houses
				monopolyHotel = propertiesCopy[monopolyPropertyId].hotel
				if monopolyHotel and houses<4:
					return False
				if abs(monopolyHouses-houses)>1:
					return False
		return True
	
	def evaluateBuyingHousesSequence(self,sequence):
		totalCurrentHouses = 0
		totalNewHouses = 0
		for propertyId,constructions in sequence:
			currentHouses = self.properties[propertyId].houses
			totalCurrentHouses+=currentHouses
			
			newHouses = currentHouses+constructions
			totalNewHouses+=newHouses
		return (totalNewHouses-totalCurrentHouses)
	
	def evaluateSellingSequence(self,sequence):
		totalCurrentHouses = 0
		totalNewHouses = 0
		for propertyId,constructions,hotel in sequence:
			if self.properties[propertyId].hotel:
				currentHouses = 0
			else:
				currentHouses = self.properties[propertyId].houses
			totalCurrentHouses+=currentHouses
			if self.properties[propertyId].hotel and not hotel:
				newHouses = 0
			else:
				newHouses = currentHouses-constructions
			totalNewHouses+=newHouses
		return (totalNewHouses-totalCurrentHouses)
			
	def getHousesRemaining(self):
		houses = MAX_HOUSES
		for prop in self.properties:
			houses -= prop.houses
		return houses

	def getHotelsRemaining(self):
		hotels = MAX_HOTELS
		for prop in self.properties:
			if (prop.hotel): hotels -= 1
		return hotels
	
	def getOwnedProperties(self, playerId):
		return [propertyId for propertyId in range(NUMBER_OF_PROPERTIES)
			if self.properties[propertyId].ownerId==playerId]

	def getConstructionValue(self,propertyId):
		return constants.board[propertyId]["build_cost"]

	""" Bunch of utilities """
	def getLivePlayers(self):
		return [playerId for playerId in self.players if not self.hasPlayerLost(playerId)]

	def getNextPlayer(self,currentPlayer):
		try:
			currentPlayerIndex = self.players.index(currentPlayer)
			return self.players[(currentPlayerIndex + 1) % TOTAL_NO_OF_PLAYERS]
		except Exception, e:
			# player not found
			raise
	
	def toTuple(self):
		return (self.turn, self.properties, self.positions,
				self.cash, self.bankrupt, self.phase, self.phasePayload, self.debt)
	
	def toJson(self):
		return json.dumps(self.toTuple())

	def __str__(self):
		return str(self.toTuple())
	
class Phase:
	BSMT = 0
	TRADE_OFFER = 1
	DICE_ROLL = 2
	BUYING = 3
	AUCTION = 4
	PAYMENT = 5
	JAIL = 6
	CHANCE_CARD = 7
	COMMUNITY_CHEST_CARD = 8
	
"""
The reason for victory:
0 = Greater assets at the end of specified number of turns.
1 = Timed Out (Could also pass while doing which action did the timeout occur)
2 = Bankruptcy from Debt to Opponent or Bank
3 = Bankruptcy from being unable to pay the fine for Jail on the third turn in Jail.
"""
class Reason:
	ASSETS = "Greater Assets"
	TIMEOUT = "Timeout"
	BANKRUPT = "Bankruptcy"
	
#state = State([1,2,3,4])
#print(state.toJson())