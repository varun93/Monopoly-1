from action import Action
from ..config import log
from ..constants import communityChestCards,chanceCards
from ..state import Phase

class HandleCards(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		phase = self.state.getPhase()
		cardId = self.state.getPhasePayload() #TODO: verify payload
		
		if phase == Phase.COMMUNITY_CHEST_CARD:
			card = communityChestCards[cardId]
			#previous phase may have been payment from jailDecision
			if self.state.getDebtToBank(currentPlayerId)>0:
				self.state.setPhase(Phase.PAYMENT)
			else:
				self.state.setPhase(Phase.NO_ACTION)
			self.state.setPhasePayload(None)
			self.handle_cards_pre_turn(card,'Chest')
		elif phase == Phase.CHANCE_CARD:
			card = chanceCards[cardId]
			#previous phase may have been payment from jailDecision
			if self.state.getDebtToBank(currentPlayerId)>0:
				self.state.setPhase(Phase.PAYMENT)
			else:
				self.state.setPhase(Phase.NO_ACTION)
			self.state.setPhasePayload(None)
			self.handle_cards_pre_turn(card,'Chance')
	
	def subscribe(self,response):
		pass
	
	"""Method handles various events for Chance and Community cards"""
	def handle_cards_pre_turn(self,card,deck):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		playerCash = self.state.getCash(currentPlayerId)
		phaseNumber = self.state.getPhase()
		updateState = False
		
		phasePayload = None
		
		if card['type'] == 1:
			#-ve represents you need to pay
			if card['money']<0:
				phaseNumber = Phase.PAYMENT
				self.state.addDebtToBank(currentPlayerId,abs(card['money']))
			else:
				playerCash += abs(card['money'])

		elif card['type'] == 2:
			#-ve represents you need to pay
			phaseNumber = Phase.PAYMENT
			if card['money']<0:
				debtAmount = abs(card['money'])
				for playerId in self.PLAY_ORDER:
					if playerId!=currentPlayerId and not self.state.hasPlayerLost(playerId):
						self.state.setDebtToPlayer(currentPlayerId,playerId,debtAmount)
			else:
				debtAmount = abs(card['money'])
				for playerId in self.PLAY_ORDER:
					if playerId!=currentPlayerId and not self.state.hasPlayerLost(playerId):
						self.state.setDebtToPlayer(playerId,currentPlayerId,debtAmount)
			
		elif card['type'] == 3:
			if card['position'] == self.JAIL:
				#sending the player to jail
				playerPosition = self.JAIL
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
			
			self.state.setPropertyOwner(propertyValue,currentPlayerId)
		
		elif card['type'] == 5:
			n_houses = 0
			n_hotels = 0
			for propertyId in range(self.BOARD_SIZE):
				if self.state.rightOwner(currentPlayerId,propertyId):
					housesCount = self.state.getNumberOfHouses(propertyId)
					if housesCount==5:
						n_hotels+=1
					else:
						n_houses+=housesCount

			debtAmount = abs(card['money'])*n_houses + abs(card['money2'])*n_hotels
			if debtAmount > 0:
				phaseNumber = Phase.PAYMENT
				self.state.addDebtToBank(currentPlayerId,debtAmount)
		
		elif card['type'] == 6:
			#Advance to nearest railroad. Pay 2x amount if owned
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
			
			updateState = True
		
		elif card['type'] == 7:
			#Advance to nearest utility. Pay 10x dice roll if owned
			if (playerPosition < 12) or (playerPosition>=28):
				if (playerPosition>=28):
					#Passes Go
					playerCash += self.PASSING_GO_MONEY
				playerPosition = 12
			elif (playerPosition < 28) and (playerPosition>=12):
				playerPosition = 28
			
			ownerId = self.state.getPropertyOwner(playerPosition)
			if not self.state.isPropertyOwned(playerPosition):
				#Unowned
				phaseNumber = Phase.BUYING
				phasePayload = playerPosition
			elif ownerId!=currentPlayerId:
				#Check if owned by opponent
				#TODO: Debug dice
				self.dice.roll(ignore=True)
				
				phaseNumber = Phase.PAYMENT
				phasePayload = playerPosition
				self.state.setDebtToPlayer(currentPlayerId,ownerId,10 * (self.dice.die_1 + self.dice.die_2))
		
		elif card['type'] == 8:
			#Go back 3 spaces
			playerPosition -= 3 
			updateState = True
		else:
			logger.info('Invalid card type {type}...'.format(type=card['type']))
		
		self.state.setPosition(currentPlayerId,playerPosition)
		self.state.setCash(currentPlayerId,playerCash)
		self.state.setPhase(phaseNumber)
		self.state.setPhasePayload(phasePayload)
		
		if phaseNumber == Phase.BUYING:
			self.context.buyProperty.setContext(self.context)
			self.context.buyProperty.publish()
		
		# make further calls
		if updateState:
			yield self.determine_position_effect()
			
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

