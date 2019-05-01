import sys
import six
import abc
from os import environ

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

@six.add_metaclass(abc.ABCMeta)
class BaseAgent(ApplicationSession):

	@inlineCallbacks
	def onJoin(self, details):
		print("Session attached!")
		
		#TODO: Configuration for these
		#Command line args
		#self.game_id = 1
		self.game_id = int(sys.argv[1])
		
		#URIs
		join_game_uri = 'com.game{}.joingame'.format(self.game_id)
		print(join_game_uri)
		
		# call a remote procedure.
		res = yield self.call(join_game_uri)
		print("The agent was assigned id: {}".format(res['agent_id']))
		self.id = res['agent_id']
		
		self.bsmIn = yield self.subscribe(self.bsmListener,res['BSM_IN'])
		self.buyIn = yield self.subscribe(self.buyListener,res['BUY_IN'])
		self.auctionIn = yield self.subscribe(self.auctionListener,res['AUCTION_IN'])
		self.jailIn = yield self.subscribe(self.jailListener,res['JAIL_IN'])
		self.tradeIn = yield self.subscribe(self.tradeListener,res['TRADE_IN'])
		self.broadcastIn = yield self.subscribe(self.broadcastListener,res['BROADCAST_IN'])
		self.respondTradeIn = yield self.subscribe(self.respondTradeListener,res['RESPOND_TRADE_IN'])
		self.startGameIn = yield self.subscribe(self.startGameListener,res['START_GAME_IN'])
		self.endGameIn = yield self.subscribe(self.endGameListener,res['END_GAME_IN'])
		if 'START_TURN_IN' in res:
			self.startTurnIn = yield self.subscribe(self.startTurnListener,res['START_TURN_IN'])
		else:
			self.startTurnIn = None
		if 'END_TURN_IN' in res:
			self.endTurnIn = yield self.subscribe(self.endTurnListener,res['END_TURN_IN'])
		else:
			self.endTurnIn = None
		
		self.endpoints = res

		#Successfully Registered. Invoke confirm_register
		response = yield self.call(res['CONFIRM_REGISTER'])
		print("Result of calling confirm_register: "+str(response))
	
	def getId(self):
		return self.id
	
	def startTurnListener(self,state):
		result = self.startTurn(state)
		self.publish(self.endpoints['START_TURN_OUT'],result)
	
	def endTurnListener(self,state):
		result = self.endTurn(state)
		self.publish(self.endpoints['END_TURN_OUT'],result)
	
	def startGameListener(self,state):
		result = self.startGame(state)
		self.publish(self.endpoints['START_GAME_OUT'],result)
	
	def endGameListener(self,winner):
		result = self.endGame(winner)
		self.publish(self.endpoints['END_GAME_OUT'],result)
		if isinstance(winner, dict):
			#The last game has completed
			self.teardownAgent()
	
	def bsmListener(self,state):
		result = self.getBSMDecision(state)
		self.publish(self.endpoints['BSM_OUT'],result)
	
	def buyListener(self,state):
		result = self.buyProperty(state)
		self.publish(self.endpoints['BUY_OUT'],result)
		
	def auctionListener(self,state):
		result = self.auctionProperty(state)
		self.publish(self.endpoints['AUCTION_OUT'],result)
	
	def jailListener(self,state):
		result = self.jailDecision(state)
		self.publish(self.endpoints['JAIL_OUT'],result)
	
	def tradeListener(self,state):
		result = self.getTradeDecision(state)
		self.publish(self.endpoints['TRADE_OUT'],result)
	
	def broadcastListener(self,state):
		self.receiveState(state)
		self.publish(self.endpoints['BROADCAST_OUT'])
	
	def respondTradeListener(self,state):
		result = self.respondTrade(state)
		self.publish(self.endpoints['RESPOND_TRADE_OUT'],result)

	def onDisconnect(self):
		print("disconnected")
		if reactor.running:
			reactor.stop()

	def teardownAgent(self):
		# cleanup
		self.bsmIn.unsubscribe()
		self.buyIn.unsubscribe()
		self.auctionIn.unsubscribe()
		self.jailIn.unsubscribe()
		self.tradeIn.unsubscribe()
		self.broadcastIn.unsubscribe()
		self.respondTradeIn.unsubscribe()
		self.startGameIn.unsubscribe()
		self.endGameIn.unsubscribe()
		if self.startTurnIn != None:
			self.startTurnIn.unsubscribe()
		if self.endTurnIn != None:
			self.endTurnIn.unsubscribe()

		self.leave()
	
	@abc.abstractmethod
	def startGame(self, state):
		"""
		Prepare for a new game.
		"""
	
	@abc.abstractmethod
	def startTurn(self, state):
		"""
		Merely indicating the start of a turn. No other intended function.
		"""
	
	@abc.abstractmethod
	def endTurn(self, state):
		"""
		Merely indicating the end of a turn. No other intended function.
		"""
	
	@abc.abstractmethod
	def getBSMDecision(self, state):
		"""
		Add code for Buy/Sell Houses,Hotels and Mortgage/Unmortgage here.
		"""
	
	@abc.abstractmethod
	def buyProperty(self, state):
		"""
		Add code to decide whether to buy a property here.
		"""

	@abc.abstractmethod
	def auctionProperty(self, state):
		"""
		Add code deciding your bid for an auction here.
		"""
	
	@abc.abstractmethod
	def jailDecision(self, state):
		"""
		Add code stating how you want to get out of jail here
		"""
	
	@abc.abstractmethod
	def getTradeDecision(self,state):
		"""
		Add code for trade proposals here.
		"""
	
	@abc.abstractmethod
	def respondTrade(self, state):
		"""
		Add code for responding to trades here.
		"""

	@abc.abstractmethod
	def receiveState(self, state):
		"""
		Function returns several info messages. You can process them here.
		"""
	
	@abc.abstractmethod
	def endGame(self, winner):
		"""
		Process the results of a completed game.
		The very last game would be a dictionary containing the agentId's and the 
		corresponding number of wins for each of them.
		"""
	
