from actions.action import Action
from config import log
from constants import board
from state import Phase

class DiceRoll(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		playerCash = self.state.getCash(currentPlayerId)
		
		if not self.diceThrown:
			#TODO: Debug dice
			self.dice.roll()
		
		if self.dice.double_counter == 3:
			self.send_player_to_jail()
		else:
			#Update player position
			playerPosition += (self.dice.die_1 + self.dice.die_2)
			
			#Passing Go
			if playerPosition>=self.BOARD_SIZE:
				playerPosition = playerPosition % self.BOARD_SIZE
				playerCash += self.PASSING_GO_MONEY
			
			self.state.setCash(currentPlayerId,playerCash)
			self.state.setPosition(currentPlayerId,playerPosition)
			self.determine_position_effect()
	
	def subscribe(self,response):
		#there is no user action here
		pass
	
	def send_player_to_jail(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		#send the player to jail and end the turn
		#Disable double
		self.dice.double = False
		log("jail","Agent "+str(currentPlayerId)+" has been sent to jail")
		self.state.setPosition(currentPlayerId,self.JAIL)
		self.state.setPhase(Phase.JAIL)
		self.state.setPhasePayload(None)
		
		self.context.receiveState.previousAction = "diceRoll"
		self.context.receiveState.nextAction = "endTurn"
		self.context.receiveState.setContext(self.context)
		self.context.receiveState.publish()
	
	"""
	Performed after dice is rolled and the player is moved to a new position.
	Determines the effect of the position and action required from the player.
	"""	 
	def determine_position_effect(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		playerCash = self.state.getCash(currentPlayerId)
		propertyClass = board[playerPosition]['class']
		
		if propertyClass == 'Street' or propertyClass == 'Railroad' or propertyClass == 'Utility':
			isPropertyOwned = self.state.isPropertyOwned(playerPosition)
			ownerId = self.state.getPropertyOwner(playerPosition)
			isPropertyMortgaged = self.state.isPropertyMortgaged(playerPosition)
			if not isPropertyOwned:
				#Unowned
				self.state.setPhase(Phase.BUYING)
				self.state.setPhasePayload(playerPosition)
				self.context.buyProperty.setContext(self.context)
				self.context.buyProperty.publish()
			else:
				if ownerId!=currentPlayerId and not isPropertyMortgaged:
					rent = self.calculateRent()
					self.state.setPhase(Phase.PAYMENT)
					self.state.setPhasePayload(playerPosition)
					self.state.setDebtToPlayer(currentPlayerId,ownerId,rent)
				
				self.context.handlePayment.setContext(self.context)
				self.context.handlePayment.publish()
			
		elif propertyClass == 'Chance' or propertyClass == 'Chest':
			if propertyClass == 'Chance':
				card = self.chance.draw_card()
				self.state.setPhase(Phase.CHANCE_CARD)
				self.state.setPhasePayload(card['id'])
			elif propertyClass == 'Chest':
				card = self.chest.draw_card()
				self.state.setPhase(Phase.COMMUNITY_CHEST_CARD)
				self.state.setPhasePayload(card['id'])
			
			#ReceiveState
			self.context.receiveState.previousAction = "diceRoll"
			self.context.receiveState.nextAction = "handleCards"
			self.context.receiveState.setContext(self.context)
			self.context.receiveState.publish()
		   
		elif propertyClass == 'Tax':
			tax = board[playerPosition]['tax']
			self.state.setPhase(Phase.PAYMENT)
			self.state.setPhasePayload(None)
			self.state.addDebtToBank(currentPlayerId,tax)
			
			self.context.handlePayment.setContext(self.context)
			self.context.handlePayment.publish()
		
		elif propertyClass == 'GoToJail':
			self.send_player_to_jail()
		
		elif propertyClass == 'Idle':
			#Represents Go,Jail(Visiting),Free Parking
			self.context.handlePayment.setContext(self.context)
			self.context.handlePayment.publish()
	
	def calculateRent(self):
		"""
		Property is not owned by current player. Calculate the rent he has to pay.
		"""
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		ownerId = self.state.getPropertyOwner(playerPosition)
		
		space = board[playerPosition]
		monopolies = space['monopoly_group_elements']
		counter = 0
		for monopoly in monopolies:
			if self.state.rightOwner(ownerId,monopoly):
				counter += 1
		
		if (space['class'] == 'Street'):
			houseCount = self.state.getNumberOfHouses(playerPosition)
			rent = space['rent'][houseCount]
			if counter==len(monopolies) and houseCount==0:
				rent = rent * 2
		
		elif (space['class'] == 'Railroad'):
			rent = space['rent'][counter]
		elif (space['class'] == 'Utility'):
			rent = space['rent'][counter]
			rent = rent * (self.dice.die_1 + self.dice.die_2)
		
		return rent
