import sys
from os import environ
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from subprocess import Popen,PIPE
import json

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
	
	def serialize(self):
		return {
			"numberOfPlayers":self.numberOfPlayers,
			"timeoutBehaviour":self.timeoutBehaviour,
			"gameId":self.gameId,
			"noOfGames":self.noOfGames,
			"gamesCompleted":self.gamesCompleted,
			"haveGamesStarted":self.haveGamesStarted,
			"haveGamesEnded":self.haveGamesEnded
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
		
	@inlineCallbacks
	def init_game(self,*args):
		numberOfPlayers = None
		timeoutBehaviour = None
		noOfGames = None
		if len(args) < 2:
			return False
		if isinstance(args[0],int) and args[0] > 2 and args[0] < 8:
			numberOfPlayers = args[0]
		if isinstance(args[1],int) and (args[1]==0 or args[1]==1):
			timeoutBehaviour = args[1]
		if isinstance(args[2],int) and args[0] > 0:
			noOfGames = args[2]
		
		if numberOfPlayers == None or timeoutBehaviour == None or noOfGames == None:
			return False
		
		self.gameid_counter += 1
		gameId = self.gameid_counter
		
		#called by the newly started adjudicator instance to provide updates about the game.
		yield self.register(self.adjudicatorCommChannel,"com.monopoly.game{}.comm_channel".format(gameId))
		
		#sys.executable gets the python executable used to start the current script
		popen_id = Popen([sys.executable,"../adjudicator/newAdjudicator.py",gameId,numberOfPlayers,timeoutBehaviour,noOfGames])
		
		game = Game(gameId,numberOfPlayers,timeoutBehaviour,noOfGames,popen_id)
		self.games_list.append(game)
		
		return True
	
	@inlineCallbacks
	def adjudicatorCommChannel(self,gameId,messageType,message):
		currentGame = None
		
		for game in self.games_list:
			if game.gameId == gameId:
				currentGame = game
				break
		
		if currentGame == None:
			return False
		
		if messageType == 0: # games for this adjudicator have started
			currentGame.haveGamesStarted = True
		elif messageType == 1:
			# all games for this adjudicator have ended
			#This would be called just before the adjudicator is shutdown
			currentGame.haveGamesEnded = True
		elif messageType == 2:
			currentGame.gamesCompleted += 1
			
		#TODO: Send these to the UI as updates
	
	def fetch_games(self):
		return json.dumps([game.serialize() for game in self.games_list])
		
		
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