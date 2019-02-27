from os import environ
from functools import partial

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner



class GameGen(ApplicationSession):
    
    #Agent has confirmed that he has registered all his methods. We can enroll the agent in the game.
    #TODO: Should we verify if these connections are active?
    def confirm_register(self,gameId,agentId):
        if self.current_no_players >= self.expected_no_players:
            return False
        
        self.current_no_players+=1
        self.agents.append(agentId)
        
        print("Agent with counter "+agentId+" for game "+gameId+" confirmed.")
        
        # this will be pulled in from the command line
        #result = yield self.runGame(["1","2"])
        #print(result)
        
        return True
        
    def generateAgentDetails(self):
        self.agentCounter+=1
        
        agent_attributes = {}
        for id,value in self.agent_info.items():
            if id == 'agent_id':
                agent_attributes[id] = value.format(self.agentCounter)
            else:
                agent_attributes[id] = value.format(self.game_id,self.agentCounter)
               
                #Create channel where the agent can confirm  his registration
                gameId = str(self.game_id)
                agentId = str(self.agentCounter)
                self.register(partial(self.confirm_register,gameId,agentId),
                    agent_attributes['confirm_register'])
               
        print("Agent with counter "+str(self.agentCounter)+" initialized.")
        return agent_attributes

    @inlineCallbacks
    def onJoin(self, details):
        print("In "+self.onJoin.__name__)
        
        #TODO: Configuration for these
        #TODO: The  agentCounter used in the URI needs to be hashed to prevent impersonation (Or some other solution)
        self.expected_no_players = 3
        self.current_no_players = 0
        self.agents = [] #Stores ids of agents in the current game
        self.game_id = 1
        
        
        self.agentCounter = 0
        self.agent_info = { 'agent_id':'{}',
                'confirm_register':'com.game{}.agent{}.confirm_register',
                'bsm':'com.game{}.agent{}.bsm',
                'respondtrade':'com.game{}.agent{}.respondtrade',
                'buy':'com.game{}.agent{}.buy',
                'auction':'com.game{}.agent{}.auction',
                'jail':'com.game{}.agent{}.jail',
                'receivestate':'com.game{}.agent{}.receivestate',
                'trade':'com.game{}.agent{}.trade'}
        
        yield self.register(self.generateAgentDetails,'com.game{}.joingame'.format(self.game_id))

        #self.leave()

    def onDisconnect(self):
        print("disconnected")
        reactor.stop()

if __name__ == '__main__':
    import six
    url = environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = u"crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(GameGen)