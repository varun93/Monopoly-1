from actions.action import Action
from state import Phase
import constants

class JailDecision(Action):
	
	def publish(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		self.agentsYetToRespond = [currentPlayerId]
		playerPosition = self.state.getPosition(currentPlayerId)
		if playerPosition != self.JAIL:
			#player is not in jail. bypass and call subscribe
			#send the player directly to diceRoll
			self.context.diceRoll.diceThrown = False
			self.context.diceRoll.setContext(self.context)
			self.context.diceRoll.publish()
		else:
			#InJail
			self.state.setPhase(Phase.JAIL)
			self.state.setPhasePayload(None)
			self.publishAction(currentPlayerId,"JAIL_IN")
	
	def subscribe(self,*args):
		agentId = None
		response = None
		if len(args)>0:
			agentId = args[0]
		if len(args)>1:
			response = args[1]
		
		if agentId and self.canAccessSubscribe(agentId):
			outOfJail,diceThrown = self.handle_in_jail_state(response)
			
			#let the player know if he is out of jail or not
			self.state.setPhasePayload(outOfJail)
			#Only for receiveState calls
			self.context.receiveState.previousAction = "jailDecision"
			if outOfJail:
				self.context.diceRoll.diceThrown = diceThrown
				self.context.receiveState.nextAction = "diceRoll"
			else:
				#player is still in jail. skip this turn.
				self.context.receiveState.nextAction = "endTurn"
			
			self.context.receiveState.setContext(self.context)
			self.context.receiveState.publish()
		else:
			print("Agent "+str(agentId)+" was not supposed to respond to jailDecision here.")
	
	"""
	Incoming action format:
	("R",) : represents rolling to get out
	("P",) : represents paying $50 to get out (BSMT should follow)
	("C", propertyNumber) : represents using a get out of jail card.
	Return values are 2 boolean values:
	1. Whether the player is out of jail.
	2. Whether there was a dice throw while handling jail state.
	"""
	def handle_in_jail_state(self,action):
		currentPlayerId = self.state.getCurrentPlayerId()
		
		if action=="R" or action=="P":
			action = (action,)
		
		if (isinstance(action, tuple) or isinstance(action, list)) and len(action)>0:
			if action[0] == 'P':
				playerCash = self.state.getCash(currentPlayerId)
				#TODO: The player may not have enough money here. Is this the correct way to implement this?
				if playerCash>=50:
					self.state.setCash(currentPlayerId,playerCash-50)
				else:
					self.state.addDebtToBank(currentPlayerId,50)
				
				self.state.setPosition(currentPlayerId,self.JUST_VISTING)
				self.state.resetJailCounter(currentPlayerId)
				return [True,False]
			
			elif action[0] == 'C':
				#Check if the player has the mentioned property card.
				if (len(action)>1) & (action[1] in [self.CHANCE_GET_OUT_OF_JAIL_FREE,self.COMMUNITY_GET_OUT_OF_JAIL_FREE]):
					
					if self.state.isPropertyOwned(action[1]) and self.state.rightOwner(currentPlayerId,action[1]):
						if action[1] == self.COMMUNITY_GET_OUT_OF_JAIL_FREE:
							self.chest.deck.append(constants.communityChestCards[4])
						elif action[1] == self.CHANCE_GET_OUT_OF_JAIL_FREE:
							self.chance.deck.append(constants.chanceCards[7])
						
						self.state.setPropertyUnowned(action[1])
						
						self.state.setPosition(currentPlayerId,self.JUST_VISTING)
						self.state.resetJailCounter(currentPlayerId)
						return [True,False]
		
		"""If both the above method fail for some reason, we default to dice roll."""
		self.dice.roll()
		if self.dice.double:
			#Player can go out
			#Need to ensure that there is no second turn for the player in this turn.
			self.dice.double = False
			self.state.setPosition(currentPlayerId,self.JUST_VISTING)
			self.state.resetJailCounter(currentPlayerId)
			return [True,True]
		
		self.state.incrementJailCounter(currentPlayerId)
		if self.state.getJailCounter(currentPlayerId)==3:
			playerCash = self.state.getCash(currentPlayerId)
			#The player has to pay $50 and get out. 
			if playerCash>=50:
				self.state.setCash(currentPlayerId,playerCash-50)
			else:
				#This is added as debt so that the player has the opportunity to resolve it.
				self.state.addDebtToBank(currentPlayerId,50)
			self.state.setPosition(currentPlayerId,self.JUST_VISTING)
			self.state.resetJailCounter(currentPlayerId)

			log("jail","Agent "+str(currentPlayerId)+" has been in jail for 3 turns. Forcing him to pay $50 to get out.")
			return [True,True]
		return [False,True]
