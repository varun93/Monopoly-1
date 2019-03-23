from functools import partial

from dice import Dice
from utils import TimeoutBehaviour,Timer

# autobahn imports
from os import environ
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

class Adjudicator(ApplicationSession):
	
	@inlineCallbacks
	def onJoin(self, details):
		"""CONFIGURATION SETTINGS"""
		self.BOARD_SIZE = 40
		self.PASSING_GO_MONEY = 200
		self.TOTAL_NO_OF_TURNS = 100
		self.INITIAL_CASH = 1500
		self.NO_OF_GAMES = 10
		
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
		
		#Constants
		self.CHANCE_GET_OUT_OF_JAIL_FREE = 40
		self.COMMUNITY_GET_OUT_OF_JAIL_FREE = 41
		self.JUST_VISTING = 10
		self.JAIL = -1
		
		self.dice = Dice()
		
				
	#Agent has confirmed that he has registered all his methods. We can enroll the agent in the game.
	#TODO: Should we verify if these connections are active?
	def outchannelListener(self,agentId):
		if self.current_no_players >= self.expected_no_players or self.gameStarted:
			return False
		
		self.current_no_players+=1
		self.agents.append(agentId)
		
		# enough people have joined. start the game.
		if self.current_no_players == self.expected_no_players:
			self.startGame(self.agents)
		
		return True
	   
	def timeoutHandler(self):
		print('In timeoutHandler')
		if not self.gameStarted:
			if self.current_no_players < self.expected_no_players:
				if self.timeout_behaviour == TimeoutBehaviour.PLAY_ANYWAY and len(self.agents)>=2:
					self.startGame(self.agents)
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
	def startGame(self,agents, end_game_uri):
		result = yield self.runGame(agents)
		print(result)
		# the reason for not notifying the agent
		# directly is to make sure that message is sent via game gen
		for agent in agents:
			print(end_game_uri)
			yield self.publish(end_game_uri,agent,result)