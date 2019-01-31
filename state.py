import random
from collections import namedtuple
from constants import board

StateTuple = namedtuple("StateTuple", "turn properties positions money bankrupt phase phaseData debt")

INITIAL_CASH = 1500
MAX_HOUSES = 32
MAX_HOTELS = 12
TOTAL_NO_OF_PLAYERS = 4
NUMBER_OF_PROPERTIES = 42

class Property:
	def __init__(self,houses,mortgaged,playerId):
		self.houses = houses
		self.mortgaged = mortgaged
		self.playerId = playerId #0 means owned by the bank

class State:

	def __init__(self, playerIds):
		TOTAL_NO_OF_PLAYERS = len(playerIds)
		
		#List of id's of all the agents in the order in which the game will take place.
		self.players = playerIds
		
		self.turn = 0
		self.properties = [Property(0,False,0)]*NUMBER_OF_PROPERTIES
		self.positions = [0]*TOTAL_NO_OF_PLAYERS
		self.cash = [INITIAL_CASH]*TOTAL_NO_OF_PLAYERS
		self.bankrupt = [False]*TOTAL_NO_OF_PLAYERS
		self.phase = Phase.BSMT
		self.phasePayload = None
		individualDebtArray = [0]*(TOTAL_NO_OF_PLAYERS+1)
		self.debt = [ individualDebtArray ]*TOTAL_NO_OF_PLAYERS
		
		self.jailCounter = [0]*TOTAL_NO_OF_PLAYERS
		self.timeoutTracker = [False]*TOTAL_NO_OF_PLAYERS
		
		#Keeping track of reason for loss and in which turn the player lost.
		"""
		The reason for victory:
		0 = Greater assets at the end of specified number of turns.
		1 = Timed Out (Could also pass while doing which action did the timeout occur)
		2 = Bankruptcy from Debt to Opponent or Bank
		3 = Bankruptcy from being unable to pay the fine for Jail on the third turn in Jail.
		"""
		self.reason = [None]*TOTAL_NO_OF_PLAYERS
		self.turn_of_loss = [-1]*TOTAL_NO_OF_PLAYERS
	
	def getCurrentPlayerIndex(self):
		return self.turn % TOTAL_NO_OF_PLAYERS
	
	def getCurrentPlayerId(self):
		return self.players[self.getCurrentPlayerIndex()]
	
	def updateTurn(self):
		self.turn+=1
	
	"""POSITION"""
	def getPosition(self,playerIndex):
		self.positions[playerIndex]
	
	def setPosition(self,playerIndex,position):
		self.positions[playerIndex] = position
	
	"""CASH"""
	def getCash(self,playerIndex):
		self.cash[playerIndex]
		
	def setCash(self,playerIndex,cash):
		self.cash[playerIndex] = cash
	
	"""BANKRUPT"""
	def hasPlayerLost(self,playerIndex):
		return self.bankrupt[playerIndex]
	
	def markPlayerLost(self,playerIndex,reason):
		self.bankrupt[playerIndex] = True
		self.reason[playerIndex] = reason
		self.turn_of_loss[playerIndex] = self.turn
	
	"""PHASE"""
	def getPhase(self,playerIndex):
		self.phase[playerIndex]
		
	def setPhase(self,playerIndex,phase):
		self.phase[playerIndex] = phase
	
	"""PHASE PAYLOAD"""
	def getPhasePayload(self,playerIndex):
		self.phase[playerIndex]
		
	def setPhasePayload(self,playerIndex,phasePayload):
		self.phasePayload[playerIndex] = phasePayload
	
	"""DEBT"""
	def getTotalDebt(self,playerIndex):
		#How should we pass the debt here?
		totalDebt = 0
		for amount in self.debt[playerIndex]:
			totalDebt+=amount
		return totalDebt
	
	def setDebtToPlayer(self,playerIndex,otherPlayer,amount):
		self.debt[playerIndex][otherPlayer+1] = amount
	
	def addDebtToBank(self,playerIndex,debt):
		self.debt[playerIndex][0]+= debt
	
	def clearDebt(self,playerIndex):
		for i in range(TOTAL_NO_OF_PLAYERS+1):
			self.debt[playerIndex][i] = 0
		
	"""JAIL COUNTER"""
	def getJailCounter(self,playerIndex):
		return self.jailCounter[playerIndex]
	
	def incrementJailCounter(self,playerIndex):
		self.jailCounter[playerIndex]+=1
	
	def resetJailCounter(self,playerIndex):
		self.jailCounter[playerIndex]=0
	
	"""PROPERTIES"""
	def getPropertyOwner(self,propertyId):
		return self.properties[propertyId].playerId
	
	def setPropertyOwner(self,playerIndex,propertyId):
		self.properties[propertyId].playerId = playerIndex
		self.properties[propertyId].houses = 0 #If a property changes ownership, it shuld always have no houses on it.
	
	def isPropertyMortgaged(self,propertyId):
		return self.properties[propertyId].mortgaged
	
	def setPropertyMortgaged(self,propertyId,mortgaged):
		self.properties[propertyId].mortgaged = mortgaged
	
	def getNumberOfHouses(self,propertyId):
		return self.properties[propertyId].houses
	
	def setNumberOfHouses(self,propertyId,count):
		self.properties[propertyId].houses = count
	
	def getOwnedProperties(self, playerIndex):
		return [propertyId for propertyId in range(NUMBER_OF_PROPERTIES)
			if self.properties[propertyId].playerId==playerIndex]
	
	"""
	This function checks the following:
	Checks if the properties are streets
	That the player owns all the properties in the monopoly and that they are all unmortgaged.
	That the end result of the buying operation results in houses being built evenly.
	If even one fault is found, the entire operation is invalidated,
	"""
	def isBuyingSequenceValid(self, playerIndex,buyingSequence):
		propertiesCopy = list(self.properties)
		for (propertyId,housesCount) in buyingSequence:
			if board[propertyId]['class']!="Street":
				return False
			
			if (propertiesCopy[propertyId].playerId!=playerIndex) or (propertiesCopy[propertyId].mortgaged):
				return False
			
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				if (propertiesCopy[monopolyPropertyId].playerId!=playerIndex) or (propertiesCopy[monopolyPropertyId].mortgaged):
					return False
			
			if propertiesCopy[propertyId].houses+housesCount>5:
				return False
			
			propertiesCopy[propertyId].houses+=housesCount
		
		for (propertyId,_) in buyingSequence:
			houses = propertiesCopy[propertyId].houses
			for monopolyPropertyId in board[propertyId]["monopoly_group_elements"]:
				monopolyHouses = propertiesCopy[monopolyPropertyId].houses
				if abs(monopolyHouses-houses)>1:
					return False
		
		return True
			
	
	def getHousesRemaining(self):
		houses = MAX_HOUSES
		for prop in self.properties:
			if (prop.houses>0) and (prop.houses<5): houses -= prop.houses
		return houses

	def getHotelsRemaining(self):
		hotels = MAX_HOTELS
		for prop in self.properties:
			if (prop.houses==5): hotels -= 1
		return hotels

	def toTuple(self):
		return StateTuple(self.turn, tuple(self.properties), tuple(self.positions),
						  tuple(self.money), self.phase, self.phaseData, tuple(self.debt))

	def __str__(self):
		return str(self.toTuple())
	
class Phase:
	BSTM = 0
	TRADE_OFFER = 1
	DICE_ROLL = 2
	BUYING = 3
	AUCTION = 4
	PAYMENT = 5
	JAIL = 6
	CHANCE_CARD = 7
	COMMUNITY_CHEST_CARD = 8
	
class Reason:
	ASSETS = "Greater Assets"
	TIMEOUT = "Timeout"
	BANKRUPT = "Bankruptcy"