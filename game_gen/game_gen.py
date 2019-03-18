import sys
from os import environ
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
from twisted.python.failure import Failure



class GameGen(ApplicationSession):
    
    @inlineCallbacks
    def onJoin(self, details):
        print("In "+self.onJoin.__name__)
        
        self.CHANCE_GET_OUT_OF_JAIL_FREE = 40
        self.COMMUNITY_GET_OUT_OF_JAIL_FREE = 41
        self.JUST_VISTING = 10
        self.JAIL = -1
        
        self.dice = None
        
        """CONFIGURATION SETTINGS"""
        self.BOARD_SIZE = 40
        self.PASSING_GO_MONEY = 200
        self.TOTAL_NO_OF_TURNS = 100
        self.INITIAL_CASH = 1500
        
        #TODO: Configuration for these
        #TODO: The  agentCounter used in the URI needs to be hashed to prevent impersonation (Or some other solution)
        self.expected_no_players = int(sys.argv[2])
        self.current_no_players = 0
        self.agents = [] #Stores ids of agents in the current game
        self.game_id = int(sys.argv[1])
        self.gameStarted = False
       
        self.game_end_uri = 'com.game{}.end_game'.format(self.game_id)
        self.agentCounter = 0
        self.agent_info = { 'agent_id':'{}',
                'confirm_register':'com.game{}.agent{}.confirm_register',
                'bsm':'com.game{}.agent{}.bsm',
                'respondtrade':'com.game{}.agent{}.respondtrade',
                'buy':'com.game{}.agent{}.buy',
                'auction':'com.game{}.agent{}.auction',
                'jail':'com.game{}.agent{}.jail',
                'receivestate':'com.game{}.agent{}.receivestate',
                'trade':'com.game{}.agent{}.trade',
                'endgame':'com.game{}.agent{}.endgame'
                }
       
        results = []
        res = yield self.register(self)
        results.extend(res)

        for res in results:
            if isinstance(res, Failure):
                print("Failed to register procedure: {}".format(res.value))
            else:
                print("registration ID {}: {}".format(res.id, res.procedure))

    #Agent has confirmed that he has registered all his methods. We can enroll the agent in the game.
    #TODO: Should we verify if these connections are active?
    def confirm_register(self,agentId):
        if self.current_no_players >= self.expected_no_players:
            return False
        
        self.current_no_players+=1
        self.agents.append(agentId)
        
        # publish the message to the adjudicator
        if self.current_no_players == self.expected_no_players:
            game_start_uri = 'com.game{}.start_game'.format(self.game_id)
            # I dont like the hardcoding here but its fine for the time being
            game_end_uri = 'com.game{}.endgame'.format(sys.argv[1])
            self.publish(game_start_uri, self.agents, game_end_uri)
        
        return True
    
    @wamp.register('com.game{}.joingame'.format(sys.argv[1]))
    def generateAgentDetails(self):
        self.agentCounter += 1
        
        agent_attributes = {}
        for agentId,value in self.agent_info.items():
            if agentId == 'agent_id':
                agent_attributes[agentId] = value.format(self.agentCounter)
            else:
                agent_attributes[agentId] = value.format(self.game_id,self.agentCounter)
                
        #Create channel where the agent can confirm  his registration
        self.register(partial(self.confirm_register,str(self.agentCounter)),
            agent_attributes['confirm_register'])
               
        print("Agent with counter "+str(self.agentCounter)+" initialized.")
        return agent_attributes

    @wamp.register('com.game{}.endgame'.format(sys.argv[1]))
    def teardownAgent(self,agent_id, result):
        self.agentCounter -= 1
        end_game_uri = self.agent_info["endgame"].format(self.game_id,agent_id)
        # game you would want to aggregate some data and send back the payload here
        self.publish(end_game_uri,result)
        
        
    def onDisconnect(self):
        if reactor.running:
            reactor.stop()

if __name__ == '__main__':
    import six
    url = environ.get("CBURL", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(GameGen)