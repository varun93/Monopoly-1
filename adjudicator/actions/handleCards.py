from action import Action
from ..config import log

class HandleCards(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		playerPosition = self.state.getPosition(currentPlayerId)
		
		#previous phase may have been payment from jailDecision
		self.state.setPhase(self.state.getPhase())
		self.state.setPhasePayload(None)
		self.handle_cards_pre_turn(card,'Chance') #Chest
	
	def subscribe(self,response):
		pass
	
	"""Method handles various events for Chance and Community cards"""
	@inlineCallbacks
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
			
			self.state.setPosition(currentPlayerId,playerPosition)
			output = self.handle_property()
			if 'phase' in output:
				phaseNumber = output['phase']
			if 'phase_properties' in output:
				phasePayload = output['phase_properties']
			if 'debt' in output:
				#We need to double rent if the player landed on opponent's property.
				self.state.setDebtToPlayer(currentPlayerId,output['debt'][0],output['debt'][1]*2)
		
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
				diceThrow = None
				if (self.diceThrows is not None) and len(self.diceThrows)>0:
					diceThrow = self.diceThrows.pop(0)
				self.dice.roll(ignore=True,dice=diceThrow)
				
				phaseNumber = Phase.PAYMENT
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
		
		if phaseNumber==Phase.BUYING:
				action = yield self.runPlayerOnStateWithTimeout(currentPlayerId,"BUY")
				action = self.typecast(action, bool, False)
				if not action:
					self.state.setPhase(Phase.AUCTION)
		
		# make further calls
		if updateState:
			yield self.determine_position_effect()

