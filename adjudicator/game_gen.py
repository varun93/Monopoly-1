import sys
from os import environ
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from subprocess import Popen,PIPE
import json
import time

class Game:
	def __init__(self,gameId,numberOfPlayers,timeoutBehaviour,noOfGames,popenId):
		self.gameId = gameId
		self.numberOfPlayers = numberOfPlayers
		self.timeoutBehaviour = timeoutBehaviour
		self.noOfGames = noOfGames
		self.popenId = popenId
		self.gamesCompleted = 0
		self.haveGamesStarted = False
		# noOfGames could be > 1. This Boolean thus represents when all these games have been completed
		self.haveGamesEnded = False
		self.playersJoined = 0
	
	def serialize(self):
		return {
			"numberOfPlayers":self.numberOfPlayers,
			"timeoutBehaviour":self.timeoutBehaviour,
			"gameId":self.gameId,
			"noOfGames":self.noOfGames,
			"gamesCompleted":self.gamesCompleted,
			"haveGamesStarted":self.haveGamesStarted,
			"haveGamesEnded":self.haveGamesEnded,
			"playersJoined":self.playersJoined
			}

class GameGen(ApplicationSession):
	
	@inlineCallbacks
	def onJoin(self, details):
		print("In "+self.onJoin.__name__)
		
		self.gameid_counter = 0
		self.games_list = []

		self.confirm_registration_handles = {}
		
		#called by the Start New Game UI
		yield self.register(self.init_game,"com.monopoly.init_game")
		yield self.register(self.fetch_games,"com.monopoly.fetch_games")
		yield self.register(self.addOurAgent,"com.monopoly.add_our_agent")
		
	@inlineCallbacks
	def init_game(self,*args):
		print("Inside init_game")
		if len(args) < 2:
			return -1
		try:
			numberOfPlayers = int(args[0])
			timeoutBehaviour = int(args[1])
			noOfGames = int(args[2])
		except:
			return -1
		if numberOfPlayers < 2 or numberOfPlayers > 8:
			return -1
		if timeoutBehaviour != 0 and timeoutBehaviour != 1:
			return -1
		if noOfGames <= 0:
			return -1
		
		self.gameid_counter += 1
		gameId = self.gameid_counter
		
		#called by the newly started adjudicator instance to provide updates about the game.
		yield self.register(self.adjudicatorCommChannel,"com.monopoly.game{}.comm_channel".format(gameId))
		
		#sys.executable gets the python executable used to start the current script
		popen_id = Popen([sys.executable,"./newAdjudicator.py",str(gameId),str(numberOfPlayers),str(timeoutBehaviour),str(noOfGames)])
		time.sleep(2)
		
		game = Game(gameId,numberOfPlayers,timeoutBehaviour,noOfGames,popen_id)
		self.games_list.append(game)
		
		return game.serialize()
	
	#Used to register the comm channel to the UI.
	#Since we don't know when the UI could come online, we need to register this beforehand.
	def stub(self,*args):
		pass
	
	#@inlineCallbacks
	def adjudicatorCommChannel(self,gameId,messageType):
		currentGame = None
		
		for game in self.games_list:
			if game.gameId == gameId:
				currentGame = game
				break
		
		if currentGame == None:
			return False
		
		message = None
		if messageType == 0: # games for this adjudicator have started
			currentGame.haveGamesStarted = True
		elif messageType == 1:
			# all games for this adjudicator have ended
			#This would be called just before the adjudicator is shutdown
			currentGame.haveGamesEnded = True
		elif messageType == 2:
			currentGame.gamesCompleted += 1
			message = currentGame.gamesCompleted
		elif messageType == 3: # an agent has joined the game
			currentGame.playersJoined += 1
			message = currentGame.playersJoined
			
		self.publish("com.monopoly.ui.comm_channel", [gameId,messageType,message])
	
	def fetch_games(self):
		print("Inside fetch_games")
		return [game.serialize() for game in self.games_list]
	
	def addOurAgent(self,*args):
		if len(args) < 1:
			return False
		try:
			gameId = int(args[0])
		except:
			return False
		
		found = False
		for game in self.games_list:
			if game.gameId == gameId:
				found = True
		if not found:
			return False
		
		#sys.executable gets the python executable used to start the current script
		popen_id = Popen([sys.executable,"./sampleAgents/TeamBoardwalk/agent_init.py",str(gameId)])
		print("Our agent was added into game #"+str(gameId))
		return True
			
		
	def onDisconnect(self):
		if reactor.running:
			reactor.stop()

if __name__ == '__main__':
	import six
	url = environ.get("CBURL", u"ws://127.0.0.1:3000/ws")
	if six.PY2 and type(url) == six.binary_type:
		url = url.decode('utf8')
	realm = environ.get('CBREALM', u'realm1')
	runner = ApplicationRunner(url, realm)
	runner.run(GameGen)