import sys
from os import environ
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from twisted.python.failure import Failure
from subprocess import Popen,PIPE

class Game:
	def __init__(self,numberOfPlayers,timeoutBehaviour,gameId,noOfGames,popenId):
		self.numberOfPlayers = numberOfPlayers
		self.timeoutBehaviour = timeoutBehaviour
		self.gameId = gameId
		self.noOfGames = noOfGames
		self.popenId = popenId

class GameGen(ApplicationSession):
	
	@inlineCallbacks
	def onJoin(self, details):
		print("In "+self.onJoin.__name__)
		
		self.gameid_counter = 0
		self.games_list = []

		self.confirm_registration_handles = {}

		self.FETCH_GAMES_URI = "com.monopoly.fetch_games"
		
		#called by the Start New Game UI
		yield self.register(self.init_game,"com.monopoly.init_game")

	def init_game(self,*args):
		numberOfPlayers = None
		timeoutBehaviour = None
		if len(args)>0 and isinstance(args[0],int) and args[0] > 2 and args[0] < 8:
			numberOfPlayers = args[0]
		if len(args)>1 and isinstance(args[1],int) and (args[1]==0 or args[1]==1):
			timeoutBehaviour = args[1]
		
		if numberOfPlayers == None or timeoutBehaviour == None:
			return False
		
		self.gameid_counter += 1
		gameId = self.gameid_counter
		
		#called by the newly started adjudicator instance to provide updates about the game.
		yield self.register(self.init_game,"com.monopoly.game{}.comm_channel".format(gameId))
		
		#sys.executable gets the python executable used to start the current script
		popen_id = Popen([sys.executable,"newAdjudicator.py",numberOfPlayers,timeoutBehaviour,gameId])
		
		game = Game(numberOfPlayers,timeoutBehaviour,gameId,popen_id)
		self.games_list.append(game)
		
		return True
	
	#
	def adjudicatorCommChannel(self,gameId,messageType,message):
		pass
	   
	@wamp.subscribe('com.game{}.endgame'.format(sys.argv[1]))
	def teardownAgent(self,agent_id, result):
		
		print("Am I here")
		self.agentCounter -= 1
		self.current_no_players -= 1

		if agent_id in self.confirm_registration_handles:
			self.confirm_registration_handles[agent_id].unregister()
		
		end_game_uri = self.agent_info["endgame"].format(self.game_id,agent_id)
		# game you would want to aggregate some data and send back the payload here
		self.publish(end_game_uri,result)
		
		
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