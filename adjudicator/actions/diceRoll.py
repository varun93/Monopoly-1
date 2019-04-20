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
			#calls endTurn action
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
			
			self.state.setPhase(Phase.DICE_ROLL)
			if self.isOption(currentPlayerId,"DICE_ROLL"):
				#sending the dice roll values to the agent
				self.state.setPhasePayload([self.dice.die_1, self.dice.die_2])
				
				#ReceiveState
				self.context.receiveState.previousAction = "diceRoll"
				self.context.receiveState.nextAction = "turnEffect"
				self.context.receiveState.setContext(self.context)
				self.context.receiveState.publish()
			else:
				self.context.turnEffect.setContext(self.context)
				self.context.turnEffect.publish()
	
	def subscribe(self,response):
		#there is no user action here
		pass
	
	def send_player_to_jail(self):
		currentPlayerId = self.state.getCurrentPlayerId()
		#send the player to jail and end the turn
		#Disable double
		self.dice.double = False
		self.dice.double_counter = 0
		log("jail","Agent "+str(currentPlayerId)+" has been sent to jail")
		self.state.setPosition(currentPlayerId,self.JAIL)
		self.state.setPhase(Phase.JAIL)
		self.state.setPhasePayload(None)
		
		self.context.receiveState.previousAction = "diceRoll"
		self.context.receiveState.nextAction = "endTurn"
		self.context.receiveState.setContext(self.context)
		self.context.receiveState.publish()
