from functools import partial

import constants
from dice import Dice
from cards import Cards
from state import State
from utils import TimeoutBehaviour,Timer

from actions.startTurn import StartTurn
from actions.jailDecision import JailDecision
from actions.receiveState import ReceiveState

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
		self.gameId = int(sys.argv[1])
		self.expectedPlayerCount = int(sys.argv[2])
		self.timeout = 300 #will wait 5 min for all players to join
		self.timeoutBehaviour = TimeoutBehaviour.STOP_GAME
		
		self.currentPlayerCount = 0
		self.agents = [] #Stores ids of agents in the current game
		
		#TODO: Sync
		self.gameStarted = False
		
		self.agentCounter = 0
		self.agent_info = {
			'agent_id':'{}',
			"inchannel" : "com.game{}.agent{}.inchannel",
			"outchannel" : "com.game{}.agent{}.outchannel",
		}
		
		#after timeout, don't wait for new players anymore
		#if enough players haven't joined, either start the game or stop it
		timer = Timer()
		timer.setTimeout(self.timeoutHandler, self.timeout)
		
				
	#Agent has confirmed that he has registered all his methods. We can enroll the agent in the game.
	#TODO: Should we verify if these connections are active?
	def outchannelListener(self,agentId):
		if self.current_no_players >= self.expected_no_players or self.gameStarted:
			return False
		
		self.current_no_players+=1
		self.agents.append(agentId)
		
		# enough people have joined. start the game.
		if self.current_no_players == self.expected_no_players:
			self.startGame()
		
		return True
	   
	def timeoutHandler(self):
		print('In timeoutHandler')
		if not self.gameStarted:
			if self.current_no_players < self.expected_no_players:
				if self.timeout_behaviour == TimeoutBehaviour.PLAY_ANYWAY and len(self.agents)>=2:
					self.startGame()
				else:
					#only one player joined or not enough people joined and game is set to exit in
					#such a case.
					self.leave()
			else:
				self.startGame(agents)
	
	#TODO: Synchronization
	@wamp.register('com.game{}.joingame'.format(sys.argv[1]))
	@inlineCallbacks
	def generateAgentDetails(self):
		self.agentCounter += 1
		
		agent_attributes = {}
		for agentId,value in self.agent_info.items():
			if agentId == 'agent_id':
				agent_attributes[agentId] = value.format(self.agentCounter)
			else:
				agent_attributes[agentId] = value.format(self.game_id,self.agentCounter)
				
		#Create channel where the agent can confirm  his registration
		subId = yield self.subscribe(partial(self.outchannelListener,str(self.agentCounter)),
			agent_attributes['outchannel'])
			   
		print("Agent with id "+str(self.agentCounter)+" initialized.")
		return agent_attributes
	
	#TODO: loop here using self.NO_OF_GAMES
	@inlineCallbacks
	def startGame(self):
		"""CONFIGURATION SETTINGS"""
		self.PASSING_GO_MONEY = 200
		self.TOTAL_NO_OF_TURNS = 100
		self.INITIAL_CASH = 1500
		self.NO_OF_GAMES = 10
		
		self.winCount = {}
		for agentId in self.agents:
			self.winCount[agentId] = 0
		
		for i in range(self.NO_OF_GAMES):
			
			#self.agents contains id's of agents in the current game
			PLAY_ORDER = agents #Stores the id's of all the players in the order of play
			TOTAL_NO_OF_PLAYERS = len(self.agents)
			staticContext = {
				"BOARD_SIZE": 40,
				"CHANCE_GET_OUT_OF_JAIL_FREE": 40,
				"COMMUNITY_GET_OUT_OF_JAIL_FREE": 41,
				"JUST_VISTING": 10,
				"JAIL": -1,
				"PLAY_ORDER": PLAY_ORDER,
				"TOTAL_NO_OF_PLAYERS": TOTAL_NO_OF_PLAYERS
			}
			
			#These will be initialized in the action
			self.dice = Dice()
			self.chest = Cards(constants.communityChestCards)
			self.chance = Cards(constants.chanceCards)
			self.state =  State(PLAY_ORDER)
			self.mortgagedDuringTrade = []
			self.winner = None

			#singleton classes for each action
			self.startTurn = StartTurn(self,staticContext)
			self.jailDecision = JailDecision(self,staticContext)
			self.receiveState = ReceiveState(self,staticContext)
			
			self.startTurn.setContext(self)
			self.startTurn.publish()
			
			
		 