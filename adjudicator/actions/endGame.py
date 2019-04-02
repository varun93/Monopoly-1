from actions.action import Action
from config import log
from constants import board

class EndGame(Action):
	
	def publish(self):
		log("game","Game #"+str(self.context.gamesCompleted)+" has ended.")
		
		resultsArray = self.final_winning_condition()
		log("win","Agent "+str(resultsArray[0])+" won the Game.")
	
		self.state.setPhasePayload(None)
			
		winner = resultsArray[0]
		self.context.winCount[winner]+=1
		#Allow the agent to make changes based on current game results
		self.context.gamesCompleted+=1
		if self.context.gamesCompleted < self.NO_OF_GAMES:
			agent_attributes = self.context.genAgentChannels("",requiredChannel = "END_GAME_IN")
			self.context.publish(agent_attributes["END_GAME_IN"], winner)
		else:
			#All the games have completed
			agent_attributes = self.context.genAgentChannels("",requiredChannel = "END_GAME_IN")
			self.context.publish(agent_attributes["END_GAME_IN"], self.context.winCount)
	
	def subscribe(self):
		if self.context.gamesCompleted >= self.NO_OF_GAMES:
			#Start the next game
			self.startGame.setContext(self.context)
			self.startGame.publish()
		else:
			#TODO: could be done more gracefully?
			self.context.shutDown()
	
	"""
	On final winner calculation, following are considered:
	Player's cash,
	Property value as on the title card,
	House and Hotel purchase value,
	Mortgaged properties at half price.
	"""
	def final_winning_condition(self):
		agentCash = {}
		agentPropertyWorth = {}
		
		for playerId in self.PLAY_ORDER:
			agentCash[playerId] = self.state.getCash(playerId)
			agentPropertyWorth[playerId] = 0
		
		for propertyId in range(40):
			#In 0 to 39 board position range
			isPropertyOwned = self.state.isPropertyOwned(propertyId)
			ownerId = self.state.getPropertyOwner(propertyId)
			houses = self.state.getNumberOfHouses(propertyId)
			mortgaged = self.state.isPropertyMortgaged(propertyId)
			
			price = board[propertyId]['price']
			build_cost = board[propertyId]['build_cost']
			
			if isPropertyOwned:
				if mortgaged:
					agentPropertyWorth[ownerId] += int(price/2)
				else:
					agentPropertyWorth[ownerId] += (price+build_cost*houses)
		
		for propertyId in [self.CHANCE_GET_OUT_OF_JAIL_FREE,self.COMMUNITY_GET_OUT_OF_JAIL_FREE]:
			isPropertyOwned = self.state.isPropertyOwned(propertyId)
			ownerId = self.state.getPropertyOwner(propertyId)
			if isPropertyOwned:
				agentPropertyWorth[ownerId] += 50
		
		#Using an array here to handle ties
		winners = []
		highestAssets = 0
		for playerId in self.PLAY_ORDER:
			turn_of_loss = self.state.getTurnOfLoss(playerId)
			if turn_of_loss==-1:
				log("win_condition","Agent "+str(playerId)+" Cash: "+str(agentCash[playerId]))
				log("win_condition","Agent "+str(playerId)+" Property Value: "+str(agentPropertyWorth[playerId]))
				playerAssets = agentCash[playerId]+agentPropertyWorth[playerId]
				if playerAssets > highestAssets:
					winners = [playerId]
					highestAssets = playerAssets
				elif playerAssets == highestAssets:
					winners.append(playerId)
			else:
				log("win_condition","Agent "+str(playerId)+" had lost in the turn: "+str(turn_of_loss))
		
		return winners
	