from action import Action
from ..config import log
from ..constants import board

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
	@inlineCallbacks
	def determine_position_effect(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		playerCash = self.state.getCash(currentPlayerId)
		turn_number = self.state.getTurn()
		propertyClass = board[position]['class']
		
		if propertyClass == 'Street' or propertyClass == 'Railroad' or propertyClass == 'Utility':
			isPropertyOwned = self.state.isPropertyOwned(playerPosition)
			ownerId = self.state.getPropertyOwner(playerPosition)
			isPropertyMortgaged = self.state.isPropertyMortgaged(playerPosition)
			if not isPropertyOwned:
				#Unowned
				phase = Phase.BUYING
				phasePayload = playerPosition
				self.context.buyProperty.setContext(self.context)
				self.context.buyProperty.publish()
			else:
				if ownerId!=currentPlayerId and not isPropertyMortgaged:
					rent = self.calculateRent()
					phase = Phase.PAYMENT
					phasePayload = playerPosition
					self.state.setDebtToPlayer(currentPlayerId,ownerId,rent)
				
				self.context.conductBSM.setContext(self.context)
				self.context.conductBSM.publish()
			
		elif propertyClass == 'Chance' or propertyClass == 'Chest':
			if propertyClass == 'Chance':
				#Chance
				card = self.chance.draw_card()
				log("cards","Chance card \""+str(card['content'])+"\" has been drawn")
				self.state.setPhase(Phase.CHANCE_CARD)
			elif propertyClass == 'Chest':
				#Community
				card = self.chest.draw_card()
				log("cards","Community Chest card \""+str(card['content'])+"\" has been drawn")
				self.state.setPhase(Phase.COMMUNITY_CHEST_CARD)
			
			self.state.setPhasePayload(card['id'])
			
			#ReceiveState
			self.context.receiveState.previousAction = "diceRoll"
			self.context.receiveState.nextAction = "handleCards"
			self.context.receiveState.setContext(self.context)
			self.context.receiveState.publish()
		   
		elif propertyClass == 'Tax':
			#Tax
			tax = board[playerPosition]['tax']
			self.state.setPhase(Phase.PAYMENT)
			self.state.setPhasePayload(None)
			self.state.addDebtToBank(currentPlayerId,tax)
			
			self.context.conductBSM.setContext(self.context)
			self.context.conductBSM.publish()
		
		elif propertyClass == 'GoToJail':
			self.send_player_to_jail()
		
		elif propertyClass == 'Idle':
			#Represents Go,Jail(Visiting),Free Parking
			self.context.conductBSM.setContext(self.context)
			self.context.conductBSM.publish()
			pass

	
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
			if counter==len(monopolies):
				rent = 10
			rent = rent * (self.dice.die_1 + self.dice.die_2)
		
		return rent
