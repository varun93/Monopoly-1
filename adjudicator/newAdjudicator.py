import sys
from functools import partial

from dice import Dice
from cards import Cards
from state import State
from constants import communityChestCards,chanceCards
from utils import TimeoutBehaviour

from actions.startGame import StartGame
from actions.endGame import EndGame
from actions.startTurn import StartTurn
from actions.jailDecision import JailDecision
from actions.receiveState import ReceiveState
from actions.diceRoll import DiceRoll
from actions.handleCards import HandleCards
from actions.buyProperty import BuyProperty
from actions.auctionProperty import AuctionProperty
from actions.handlePayment import HandlePayment
from actions.conductBSM import ConductBSM
from actions.endTurn import EndTurn

# autobahn imports
from os import environ
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class Adjudicator(ApplicationSession):
	
	@inlineCallbacks
	def onJoin(self, details):
		#extra stuff
		#TODO: Configuration for these
		#TODO: The  agentCounter used in the URI needs to be hashed to prevent impersonation (Or some other solution)
		#self.gameId = int(sys.argv[1])
		#self.expectedPlayerCount = int(sys.argv[2])
		self.gameId = 1
		self.expectedPlayerCount = 2
		
		self.TIMEOUT = 300 #will wait 5 min for all players to join
		self.timeoutBehaviour = TimeoutBehaviour.STOP_GAME
		
		self.currentPlayerCount = 0
		self.agents = [] #Stores ids of agents in the current game
		
		#TODO: Sync
		self.gameStarted = False
		
		self.agentCounter = 0
		self.agent_info = {
			'agent_id':'{}',
			"BSM_IN" : "monopoly.game{}.agent{}.bsm.in",
			"BSM_OUT" : "monopoly.game{}.agent{}.bsm.out",
            "BUY_IN" : "monopoly.game{}.agent{}.buy.in",
            "BUY_OUT" : "monopoly.game{}.agent{}.buy.out",
            "AUCTION_IN" : "monopoly.game{}.auction.in",
            "AUCTION_OUT" : "monopoly.game{}.agent{}.auction.out",
            "JAIL_IN" : "monopoly.game{}.agent{}.jail.in",
            "JAIL_OUT" : "monopoly.game{}.agent{}.jail.out",
            "TRADE_IN" : "monopoly.game{}.agent{}.trade.in",
            "TRADE_OUT" : "monopoly.game{}.agent{}.trade.out",
            "BROADCAST_IN" : "monopoly.game{}.receivestate.in",
            "BROADCAST_OUT" : "monopoly.game{}.agent{}.receivestate.out",
            "RESPOND_TRADE_IN" : "monopoly.game{}.agent{}.respondtrade.in",
			"RESPOND_TRADE_OUT" : "monopoly.game{}.agent{}.respondtrade.out",
			"CONFIRM_REGISTER" : "monopoly.game{}.agent{}.confirmregister",
			"START_GAME_IN": "monopoly.game{}.startgame.in",
			"START_GAME_OUT": "monopoly.game{}.agent{}.startgame.out",
			"END_GAME_IN" : "monopoly.game{}.endgame.in",
			"END_GAME_OUT" : "monopoly.game{}.agent{}.endgame.out",
		}
		
		#after timeout, don't wait for new players anymore
		#if enough players haven't joined, either start the game or stop it
		self.timeoutId = reactor.callLater(self.TIMEOUT, self.timeoutHandler)
		
		yield self.register(self.generateAgentDetails,'com.game{}.joingame'.format(self.gameId))
		
				
	#Agent has confirmed that he has registered all his methods. We can enroll the agent in the game.
	#TODO: Should we verify if these connections are active?
	def confirmRegisterListener(self,agentId):
		if self.currentPlayerCount >= self.expectedPlayerCount or self.gameStarted:
			return False
		
		self.currentPlayerCount+=1
		self.agents.append(agentId)
		print("Current Player Count: {}".format(self.currentPlayerCount))
		
		# enough people have joined. start the game.
		if self.currentPlayerCount == self.expectedPlayerCount:
			self.gameStarted = True
			self.timeoutId.cancel()
			self.startGame()
		
		return True
	   
	def timeoutHandler(self):
		print('In timeoutHandler')
		if not self.gameStarted:
			if self.currentPlayerCount < self.expectedPlayerCount:
				if self.timeoutBehaviour == TimeoutBehaviour.PLAY_ANYWAY and len(self.agents)>=2:
					self.startGame()
				else:
					#only one player joined or not enough people joined and game is set to exit in
					#such a case.
					self.leave()
			else:
				self.startGame(agents)
	
	#TODO: Synchronization
	@inlineCallbacks
	def generateAgentDetails(self):
		self.agentCounter += 1
		agent_attributes = self.genAgentChannels(self.agentCounter)
				
		#Create channel where the agent can confirm  his registration
		self.confirmReg = yield self.register(partial(self.confirmRegisterListener,str(self.agentCounter)),
			agent_attributes['CONFIRM_REGISTER'])
			   
		print("Agent with id "+str(self.agentCounter)+" initialized.")
		return agent_attributes
	
	def genAgentChannels(self,agentId,requiredChannel = None):
		agent_attributes = {}
		if requiredChannel == None:
			for channel,value in self.agent_info.items():
				if channel == 'agent_id':
					agent_attributes[channel] = value.format(agentId)
				elif channel == "AUCTION_IN" or channel == "BROADCAST_IN":
					agent_attributes[channel] = value.format(self.gameId)
				else:
					agent_attributes[channel] = value.format(self.gameId,agentId)
		else:
			if requiredChannel == 'agent_id':
				agent_attributes[requiredChannel] = self.agent_info[requiredChannel].format(agentId)
			elif requiredChannel == "AUCTION_IN" or requiredChannel == "BROADCAST_IN" or requiredChannel == "START_GAME_IN" or requiredChannel == "END_GAME_IN":
				agent_attributes[requiredChannel] = self.agent_info[requiredChannel].format(self.gameId)
			else:
				agent_attributes[requiredChannel] = self.agent_info[requiredChannel].format(self.gameId,agentId)
		return agent_attributes
	
	def shutDown(self):
		self.confirmReg.unregister()
		for subscribeKey in self.subscribeKeys:
			subscribeKey.unsubscribe()
		self.leave()
	
	#Supposedly called after we call self.leave()
	def onDisconnect(self):
		if reactor.running:
			reactor.stop()
	
	#TODO: loop here using self.NO_OF_GAMES
	@inlineCallbacks
	def startGame(self):
		"""CONFIGURATION SETTINGS"""
		self.PASSING_GO_MONEY = 200
		self.TOTAL_NO_OF_TURNS = 100
		self.INITIAL_CASH = 1500
		self.NO_OF_GAMES = 2
		self.gamesCompleted = 0
		
		self.winCount = {}
		for agentId in self.agents:
			self.winCount[agentId] = 0
			
		#self.agents contains id's of agents in the current game
		PLAY_ORDER = [agentId for agentId in self.agents] #Stores the id's of all the players in the order of play
		#There is a wierd error where if I use the shallow copy of self.agents, it could later have at first all the agent ids but later lose some of the ids.
		#So, need to do a deep copy here, in action and in state. When I did a deep copy just here and in action, it caused an error in state
		#which should never have happened but did.
		#Lesson: do deep copy of arrays when dealing with multiple threads?
		staticContext = {
			"PLAY_ORDER": PLAY_ORDER,
			"PASSING_GO_MONEY": self.PASSING_GO_MONEY,
			"TOTAL_NO_OF_TURNS": self.TOTAL_NO_OF_TURNS,
			"INITIAL_CASH": self.INITIAL_CASH,
			"NO_OF_GAMES": self.NO_OF_GAMES
		}
		
		self.dice = Dice()
		self.chest = Cards(communityChestCards)
		self.chance = Cards(chanceCards)
		self.state =  State(PLAY_ORDER)
		self.mortgagedDuringTrade = []
		self.winner = None

		#singleton classes for each action
		self.startGame = StartGame(staticContext)
		self.endGame = EndGame(staticContext)
		self.startTurn = StartTurn(staticContext)
		self.jailDecision = JailDecision(staticContext)
		self.receiveState = ReceiveState(staticContext)
		self.diceRoll = DiceRoll(staticContext)
		self.handleCards = HandleCards(staticContext)
		self.buyProperty = BuyProperty(staticContext)
		self.auctionProperty = AuctionProperty(staticContext)
		self.handlePayment = HandlePayment(staticContext)
		self.conductBSM = ConductBSM(staticContext)
		#self.trade = Trade(staticContext)
		#self.respondTrade = RespondTrade(staticContext)
		self.endTurn = EndTurn(staticContext)
		self.subscribeKeys = []
		
		for agentId in PLAY_ORDER:
			agent_attributes = self.genAgentChannels(agentId)
			sub = yield self.subscribe(partial(self.startGame.subscribe,agentId),
			agent_attributes['START_GAME_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.endGame.subscribe,agentId),
			agent_attributes['END_GAME_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.jailDecision.subscribe,agentId),
			agent_attributes['JAIL_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.receiveState.subscribe,agentId),
			agent_attributes['BROADCAST_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.buyProperty.subscribe,agentId),
			agent_attributes['BUY_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.auctionProperty.subscribe,agentId),
			agent_attributes['AUCTION_OUT'])
			self.subscribeKeys.append(sub)
			sub = yield self.subscribe(partial(self.conductBSM.subscribe,agentId),
			agent_attributes['BSM_OUT'])
			self.subscribeKeys.append(sub)
			#sub = yield self.subscribe(partial(self.trade.subscribe,agentId),
			#agent_attributes['TRADE_OUT'])
			#self.subscribeKeys.append(sub)
			#sub = yield self.subscribe(partial(self.respondTrade.subscribe,agentId),
			#agent_attributes['RESPOND_TRADE_OUT'])
			#self.subscribeKeys.append(sub)
		
		self.startGame.setContext(self)
		self.startGame.publish()
	
if __name__ == '__main__':
	import six
	url = environ.get("CBURL", u"ws://127.0.0.1:3000/ws")
	if six.PY2 and type(url) == six.binary_type:
		url = url.decode('utf8')
	realm = environ.get('CBREALM', u'realm1')
	runner = ApplicationRunner(url, realm)
	runner.run(Adjudicator)
			
			
		 