from config import log
from dice import Dice
import constants
from cards import Cards
import copy
# import timeout_decorator
from state import State,Phase,Reason

# autobahn imports
from os import environ
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

    
class Component(ApplicationSession):
    """
    An application component calling the different backend procedures.
    """
    
    @inlineCallbacks
    def startGame(self,agents, end_game_uri):
        result = yield self.runGame(agents)
        print(result)
        # the reason for not notifying the agent
        # directly is to make sure that message is sent via game gen
        for agent in agents:
        	print(end_game_uri)
        	yield self.publish(end_game_uri,agent,result)
    
        
    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")
        
        self.CHANCE_GET_OUT_OF_JAIL_FREE = 40
        self.COMMUNITY_GET_OUT_OF_JAIL_FREE = 41
        
        self.BOARD_SIZE = 40
        self.PASSING_GO_MONEY = 200
        
        self.JUST_VISTING = 10
        self.OWNED_BY_BANK = -1
        self.JAIL = -1
        
        self.dice = None
        
        """CONFIGURATION SETTINGS"""
        self.TOTAL_NO_OF_TURNS = 100
        self.INITIAL_CASH = 1500
        
        self.game_id = 1
        self.game_start_uri = 'com.game{}.start_game'.format(self.game_id)
        yield self.subscribe(self.startGame, self.game_start_uri)
        
        # this will be pulled in from the command line
        # result = yield self.runGame(["1","2"])
        # print(result)

        # self.leave()

    def onDisconnect(self):
        print("disconnected")
        if reactor.running:
            reactor.stop()

    """
    STATE PROPERTIES
    """
    # def getPlayer(self,playerId):
    #     if playerId in self.agents:
    #         return
    #     # for agent in self.agents:
    #         if agent.id==playerId:
    #             return agent
    #     return None
        
    def updateState(self, state, dimensionOneIndex, dimensionTwoIndex, valueToUpdate):
        if dimensionTwoIndex is None:
            state[dimensionOneIndex] = valueToUpdate
        else:
            state[dimensionOneIndex][dimensionTwoIndex] = valueToUpdate
    
    def transformState(self,state):
        transformedState = []

        for element in state:
            if isinstance(element, list):
                transformedState.append(tuple(element))
            elif isinstance(element, dict):
                transformedState.append(tuple([element[1] for element in element.items()]))
            else:
                transformedState.append(element)

        return tuple(transformedState)
    
    """
    Validation function which checks if the variable `var` can be typecast to datatype `thetype`.
    If there was any exception encountered, return the default value specified
    """
    def typecast(self,val,thetype,default):
        try:
            if (thetype == bool) and not isinstance(val, thetype):
                return default
            return thetype(val)
        except:
            return default
        
    #Function checks cash passed in through actions by the agent.
    #If cash can't be typecast to int, the cash amount is considered invalid and invalid flows for defaulting would take place.
    def check_valid_cash(self,cash):
        try:
            cash = int(cash)
        except:
            return 0
        if cash < 0:
            return 0
        return cash
    
    #Generator for circular range
    def crange(self,start, end, modulo):
        if start > end:
            while start < modulo:
                yield start
                start += 1
            start = 0   
        while start <= end:
            yield start
            start += 1

    def conductBSM(self):

        """Returns the type of action. Also checks if the action is valid."""
        def checkActionType(action):
            if not ( isinstance(action, list) or isinstance(action, tuple) ) or len(action)<2:
                return "N"
            
            type = action[0]
            if type=="BHS":
                if not ( isinstance(action[1], list) or isinstance(action[1], tuple) ):
                    return "N"
                else:
                    for prop in action[1]:
                        if not ( isinstance(prop, list) or isinstance(prop, tuple) ) or len(prop)<2:
                            return "N"
                        else:                           
                            firstElem = self.typecast(prop[0],int,-1)
                            secondElem = self.typecast(prop[1],int,-1)
                            if firstElem<0 or firstElem>self.BOARD_SIZE-1:
                                return "N"
                            if secondElem<0 or secondElem>4:
                                return "N"
            elif type=="S":
                if not ( isinstance(action[1], list) or isinstance(action[1], tuple) ):
                    return "N"
                else:
                    for prop in action[1]:
                        if not ( isinstance(prop, list) or isinstance(prop, tuple) ) or len(prop)<3:
                            return "N"
                        else:                           
                            firstElem = self.typecast(prop[0],int,-1)
                            secondElem = self.typecast(prop[1],int,-1)
                            thirdElem = self.typecast(prop[2], bool, False)
                            if firstElem<0 or firstElem>self.BOARD_SIZE-1:
                                return "N"
                            if secondElem<0 or secondElem>4:
                                return "N"
            elif type == "M" or type=="BHT":
                if not isinstance(action[1], list) and not isinstance(action[1], tuple):
                    return "N"
                else:
                    for prop in action[1]:
                        firstElem = self.typecast(prop,int,-1)
                        if firstElem<0 or firstElem>self.BOARD_SIZE-1:
                            return "N"
            return type
            
        def hasBuyingCapability(playerId,properties):
            playerCash = self.state.getCash(playerId)
            for propertyId,constructions in properties:
                space = constants.board[propertyId]
                playerCash -= space['build_cost']*constructions
                if playerCash < 0:
                    break
            return playerCash >= 0
                        
        # house can be built only if you own a monopoly of colours 
        # double house can be built only if I have built one house in each colour 
        # order of the tuples to be taken into account
        def handleBuyHouses(playerId,properties):
            playerCash = self.state.getCash(playerId)
            for propertyId,constructions in properties:
                houseCount = self.state.getNumberOfHouses(propertyId)
                houseCount += constructions
                playerCash -= (constants.board[propertyId]['build_cost']*constructions)
                self.state.setNumberOfHouses(propertyId,houseCount)
            self.state.setCash(playerId,playerCash)
            return True

        def handleSell(playerId,properties):
            playerCash = self.state.getCash(playerId)
            
            for propertyId,constructions,hotel in properties:
                space = constants.board[propertyId]
                if hotel: constructions+=1
                houseCount = self.state.getNumberOfHouses(propertyId)
                houseCount -= constructions
                playerCash += int(space['build_cost']*0.5*constructions)
                self.state.setNumberOfHouses(propertyId,houseCount)
            
            self.state.setCash(playerId,playerCash)
            return True

        # If property is mortgaged, player gets back 50% of the price.
        # If the player tries to unmortgage something and he doesn't have the money, the entire operation fails.
        # If the player tries to mortgage an invalid property, entire operation fails.
        @inlineCallbacks
        def handleMortgage(playerId,properties):
            playerCash = self.state.getCash(playerId)
            mortgageRequests = []
            unmortgageRequests = []
            
            for propertyId in properties:
                if self.state.getPropertyOwner(propertyId)!=playerId:
                    return False
                
                #It could be that the player is getting money to unmortgage a property 
                #by mortgaging other properties. Hence, processing mortgage requests first.
                if self.state.isPropertyMortgaged(propertyId):
                    unmortgageRequests.append(propertyId)
                else:
                    mortgageRequests.append(propertyId)
            
            for propertyId in mortgageRequests:
                #There should be no houses on a property to be mortgaged or in any other property in the monopoly.
                if self.state.getNumberOfHouses(propertyId)>0:
                    return False
                space = constants.board[propertyId]
                for monopolyPropertyId in space["monopoly_group_elements"]:
                    if self.state.getNumberOfHouses(propertyId)>0:
                        return False
                
                mortagePrice = int(constants.board[propertyId]['price']/2)
                playerCash += mortagePrice
                log("bsm","Player "+str(playerId)+" wants to mortgage.")
                
            for propertyId in unmortgageRequests:
                unmortgagePrice = int(constants.board[propertyId]['price']/2)   

                if propertyId in self.mortgagedDuringTrade:
                    self.mortgagedDuringTrade.remove(propertyId)
                else:
                    unmortgagePrice = int(unmortgagePrice*1.1)

                if playerCash >= unmortgagePrice:
                    playerCash -= unmortgagePrice 
                else:
                    return False
                
                log("bsm","Player "+str(playerId)+" wants to unmortgage.")
            
            log("bsm",str(properties))  
            for propertyId in properties:
                self.state.setPropertyMortgaged(propertyId,not self.state.isPropertyMortgaged(propertyId))
            self.state.setCash(playerId,playerCash)
        
        """
        BSMT will be carried out as decision rounds where each player is asked for his BSMT action during that round.
        If all the player's don't want to take BSMT actions in a given round, then the BSMT phase ends.
        If a player decides he doesn't want to take any BSMT actions in a given decision round, he can still make BSMT actions in later decision rounds.
        This is done so that he can react to the BSMT decisions made by other players.
        TODO:
        Find a way to ensure that BSMT doesn't go on forever.
        """
        currentPlayerIndex = self.state.getCurrentPlayerIndex()
        
        """Currently, BSM could go on forever."""
        while True:
            mortgageRequests = []
            buyingHousesRequests = []
            buyingHotelsRequests = []
            sellingRequests = []
            
            """Getting the actions for BSM from all the players"""
            actionCount=0
            for i in self.crange(currentPlayerIndex,currentPlayerIndex-1,self.TOTAL_NO_OF_PLAYERS):
                playerId = self.PLAY_ORDER[i]
                if not self.state.hasPlayerLost(playerId):
                    action = yield self.runPlayerOnStateWithTimeout(playerId,"BSM")
                    actionType = checkActionType(action) #Some basic validation like syntax,type checking and value range.
                    if actionType=="M":
                        mortgageRequests.append((playerId,action[1]))
                        actionCount+=1
                    elif actionType=="BHS":
                        if self.state.isBuyingHousesSequenceValid(playerId,action[1]) and hasBuyingCapability(playerId,action[1]):
                            buyingHousesRequests.append((playerId,action[1]))
                            log("bsm","Player "+str(playerId)+" wants to buy houses.")
                            log("bsm",str(action[1]))
                            actionCount+=1
                    elif actionType=="BHT":
                        if self.state.isBuyingHotelSequenceValid(playerId,action[1]):
                            buyingHotelsRequests.append((playerId,action[1]))
                            log("bsm","Player "+str(playerId)+" wants to buy hotels.")
                            log("bsm",str(action[1]))
                            actionCount+=1
                    elif actionType=="S":
                        if self.state.isSellingSequenceValid(playerId,action[1]):
                            sellingRequests.append((playerId,action[1]))
                            log("bsm","Player "+str(playerId)+" wants to sell houses/hotels.")
                            log("bsm",str(action[1]))
                            actionCount+=1
            
            if actionCount==0:
                break #Stop BSM if there are no valid BSM requests during a given turn
            
            """Selling Requests"""
            finishedSellingRequests = []
            for playerId,request in sellingRequests:
                housesNeeded,hotelsNeeded = self.state.evaluateSellingSequence(request)
                if housesNeeded<=0 and hotelsNeeded<=0:
                    handleSell(playerId, request)
                    finishedSellingRequests.append(playerId)
            sellingRequests = [entry for entry in sellingRequests if entry[0] not in finishedSellingRequests]
            
            housesRemaining = self.state.getHousesRemaining()
            housesNeededForBHS = 0
            for _,request in buyingHousesRequests:
                housesNeededForBHS += self.state.evaluateBuyingHousesSequence(request)
            housesRemaining -= housesNeededForBHS
            
            for playerId,request in sellingRequests:
                housesNeeded,hotelsNeeded = self.state.evaluateSellingSequence(request)
                if housesNeeded<=housesRemaining:
                    handleSell(playerId, request)
                    housesRemaining-=housesNeeded
                else: break
            
            """Mortgage/Unmortgage requests"""
            for playerId,mortgageRequest in mortgageRequests:
                yield handleMortgage(playerId,mortgageRequest)
            
            """Buying Hotels Requests"""
            hotelsRemaining = self.state.getHotelsRemaining()
            hotelsForBHT = 0
            for _,request in buyingHotelsRequests:
                hotelsForBHT += len(request)
            if hotelsRemaining-hotelsForBHT>=0:
                for playerId,request in buyingHotelsRequests:
                    self.state.buyHotelSequence(playerId,request)
            else:
                #TODO: AUCTION FOR HOTELS
                #All the hotel requests are in: buyingHotelsRequests
                self.auctionInBSM(buyingHotelsRequests,"hotels")
            
            """Buying Houses Requests"""
            housesRemaining = self.state.getHousesRemaining()
            if housesRemaining-housesNeededForBHS>=0:
                for playerId,request in buyingHousesRequests:
                    handleBuyHouses(playerId,request)
            else:
                #TODO: AUCTION FOR HOUSES
                #All the hotel requests are in: buyingHousesRequests
                self.auctionInBSM(buyingHousesRequests)
    
    """ ACTION METHODS """
    @inlineCallbacks
    def conductTrade(self):
        def validPropertyToTrade(playerId, propertyId):
            propertyId = self.typecast(propertyId,int,-1)
            if propertyId<0 or propertyId>self.BOARD_SIZE-1:
                return False
            if not  self.state.rightOwner(playerId,propertyId):
                return False
            if self.state.getNumberOfHouses(propertyId) > 0:
                return False
            return True
        
        #Syntax: (otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest)
        def validateTradeAction(action):
            if not ( isinstance(action, list) or isinstance(action, tuple) ) or len(action)<5:
                return False
            
            otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = action
            currentPlayerId = self.state.getCurrentPlayerId()
            
            passed = False
            if otherAgentId == currentPlayerId:
                return False
            for playerId in self.PLAY_ORDER:
                if otherAgentId == playerId:
                    passed = True
                    break
            if not passed:
                return False
            
            cashOffer = self.check_valid_cash(cashOffer)
            cashRequest = self.check_valid_cash(cashRequest)
            currentPlayerCash = self.state.getCash(currentPlayerId)
            otherPlayerCash = self.state.getCash(otherAgentId)
            if cashOffer > currentPlayerCash:
                return False
            if cashRequest > otherPlayerCash:
                return False
            
            if not isinstance(propertiesOffer, list) and not isinstance(propertiesOffer, tuple):
                    return False
            else:
                for propertyId in propertiesOffer:
                    if not validPropertyToTrade(currentPlayerId, propertyId):
                        return False
            
            if not isinstance(propertiesRequest, list) and not isinstance(propertiesRequest, tuple):
                    return False
            else:
                for propertyId in propertiesRequest:
                    if not validPropertyToTrade(otherAgentId, propertyId):
                        return False
            
            return True
        
        currentPlayerIndex = self.state.getCurrentPlayerIndex()

        while True:
            actionCount=0
            for i in self.crange(currentPlayerIndex,currentPlayerIndex-1,self.TOTAL_NO_OF_PLAYERS):
                playerId = self.PLAY_ORDER[i]
                if not self.state.hasPlayerLost(playerId):
                    action = yield self.runPlayerOnStateWithTimeout(playerId,"TRADE")
                    validTrade = yield validateTradeAction(action)
                    if validTrade:
                        otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest = action
                        yield self.handleTrade(playerId, otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest)
                        actionCount+=1

            if actionCount==0:
                break

    @inlineCallbacks
    def handleTrade(self,agentId,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest):

        previousPayload = self.state.getPhasePayload()
        
        cashRequest = self.check_valid_cash(cashRequest)
        cashOffer = self.check_valid_cash(cashOffer)
        
        #Ask the other agent whether he accepts the trade.
        phasePayload = [agentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest]
        self.state.setPhasePayload(phasePayload)
        tradeResponse = yield self.runPlayerOnStateWithTimeout(otherAgentId,"RESPOND_TRADE")
        print("TRADE", tradeResponse)
        tradeResponse = self.typecast(tradeResponse, bool, False)
        
        # if the trade was successful update the cash and property status
        if tradeResponse:
            currentPlayerCash =  self.state.getCash(agentId)
            otherPlayerCash = self.state.getCash(otherAgentId)

            currentPlayerCash += (cashRequest - cashOffer)
            otherPlayerCash += (cashOffer - cashRequest)
            
            self.state.setCash(agentId,currentPlayerCash)
            self.state.setCash(otherAgentId,otherPlayerCash)

            for propertyRequest in propertiesRequest:
                self.state.setPropertyOwner(propertyRequest,agentId)
            for propertyOffer in propertiesOffer:
                self.state.setPropertyOwner(propertyOffer,otherAgentId)
                
            #Handle mortgaged properties that were involved in the trade after transferring ownership
            mortgagedProperties = list(filter(lambda propertyId : self.state.isPropertyMortgaged(propertyId), propertiesOffer + propertiesRequest))
            for mortgagedProperty in mortgagedProperties:
                if mortgagedProperty not in self.mortgagedDuringTrade:
                    self.mortgagedDuringTrade.append(mortgagedProperty)
                    space = constants.board[mortgagedProperty]
                    propertyPrice = space['price']
                    mortgagedPrice = int(propertyPrice/2)
                    agentInQuestion = self.state.getPropertyOwner(mortgagedProperty)

                    agentsCash = self.state.getCash(agentInQuestion)
                    agentsCash -= int(mortgagedPrice*0.1)
                    self.state.setCash(agentInQuestion,agentsCash)
            
        #Receive State
        phasePayload = [tradeResponse,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest]
        self.state.setPhasePayload(phasePayload)
        yield self.runPlayerOnStateWithTimeout(agentId,"INFO")
        self.state.setPhasePayload(previousPayload)
        return True

    # mortgageDuringTrade 
    # buy 
    # while there is no response from the one of the players keep querying
    # 

    """
    Note : this is simulating real auction; commented for the time being 
    """
    # def start_auction(self):
    #   auctionedProperty = self.state.getPhasePayload()
    #   highestBid = 10
    #   currentParticipant = self.state.getCurrentPlayerId()
    #   auctionWinner = currentParticipant
    #   livePlayers = self.state.getLivePlayers()
        
    #   while len(livePlayers) > 1:

    #       currentParticipantIndex = livePlayers.index(currentParticipant) 
    #       currentParticipant = livePlayers[(currentParticipantIndex + 1) % len(livePlayers)]
    #       currentBid = None

    #       if self.state.getCash(currentParticipant) > highestBid:
    #           phasePayload = [auctionedProperty,auctionWinner]
    #           ## NOTE: !!set additional payload if needed
    #           self.state.setPhase(self.PHASE_NUMBER_INDEX)
    #           self.state.setPhasePayload(phasePayload)
    #           currentBid = self.runPlayerOnStateWithTimeout(currentParticipant)
            
    #       if currentBid and currentBid > highestBid:
    #           highestBid = currentBid
    #           auctionWinner = currentParticipant
    #       else:
    #           # remove the current player
    #           # yes you could use livePlayers.remove(currentParticipant) trying to avoid mutation 
    #           livePlayers = list(filter(lambda playerId : playerId != currentParticipant, livePlayers))
        
    #   auctionWinnerCurrentCash = self.state.getCash(auctionWinner)
    #   self.state.setCash(auctionWinner,auctionWinnerCurrentCash - highestBid)
    #   self.state.setPropertyOwner(auctionedProperty,auctionWinner)

        # return [True, True]
    
    """
    Accepts the actions of the blind auction from both players and performs it.
    NOTE: The expected type of action is int. If the input is float, it will be typecast.
    If the action is in some other type, following rules will be applied:
        If opponent got the type of action wrong, current player wins.
        else Opponent wins. i.e., opponent would win even if his action has incorrect type
        as long as the current player also made a mistake in the type of his action
    """ 
    @inlineCallbacks
    def handle_auction(self,auctionedProperty):
        
        currentPlayerId = self.state.getCurrentPlayerId()
        livePlayers = self.state.getLivePlayers()
        
        #By default, the player who started the auction would win and he would have to pay $1.
        winner = currentPlayerId
        winningBid = 1

        for participant in livePlayers:
            # asking for each participant for the bid
            auctionBid = yield self.runPlayerOnStateWithTimeout(participant,"AUCTION")
            auctionBid = self.check_valid_cash(auctionBid)
            playerCash = self.state.getCash(participant)
            
            #Only if the player has enough money should his bid be considered valid
            if auctionBid and auctionBid > winningBid and playerCash >= auctionBid:
                winningBid = auctionBid
                winner = participant
            
        log("auction","Player "+str(winner)+" won the Auction")
        
        playerCash = self.state.getCash(winner)
        playerCash -= winningBid
        self.state.setCash(winner,playerCash)
        self.state.setPropertyOwner(auctionedProperty,winner)   
        
        #Receive State
        phasePayload = [auctionedProperty,winner,winningBid]
        self.state.setPhasePayload(phasePayload)
        yield self.broadcastState()

    # [(1,4,2),(2,6,1),(3,8,1),(4,9,1)]
    # Triple of playerId, propertyId, numberOfConstructions
    def auctionInBSM(self,buyingDecisions,auctionEntity = "houses"):

        """
            Bunch of small utitilies
        """ 
        def updateBuyingDecisions(buyingDecisions,auctionWinner,propertySite):

            def mapper(triple):
                
                (playerId,propertyId,constructions) = triple
                
                if playerId == auctionWinner and propertyId == propertySite:
                    return (playerId,propertyId,constructions - 1)
                            
                return (playerId,propertyId,constructions)

            buyingDecisions = list(map(mapper, buyingDecisions))
            return list(filter(lambda triple :  triple[2] > 0,buyingDecisions)) 


        def updateWinnerCash(auctionWinner, bidValue):
            auctionWinnerCurrentCash = self.state.getCash(auctionWinner)
            self.state.setCash(auctionWinner,auctionWinnerCurrentCash - bidValue)

        def updateWinnerProperty(auctionedProperty):
            currentConstructions = 4
            
            if auctionEntity == "houses":
                currentConstructions = self.state.getNumberOfHouses(auctionedProperty)
            
            self.state.setNumberOfHouses(auctionedProperty, currentConstructions + 1)
        
        def getConstructionsRemaining():

            if auctionEntity == "houses":
                return self.state.getHousesRemaining()
            
            return self.state.getHotelsRemaining()

        def transformBuyingDecisions():

            # not doing any checks; to check if the the list is valid 
            def mapper(buyingDecision):
                if auctionEntity == "houses":
                    return (buyingDecision[0],buyingDecision[1][0],buyingDecision[1][1])

                return (buyingDecision[0], buyingDecision[1][0],1)

            return list(map(mapper,buyingDecisions))


        """
            End of Utilities;
            Start of auction logic 
        """

        buyingDecisions = transformBuyingDecisions()
        constructionsRemaining = getConstructionsRemaining()

        while constructionsRemaining:

            highestBid = min(list(map(lambda triple: self.state.getConstructionValue(triple[1]),buyingDecisions))) 
            interestedParticipants = list(set(map(lambda triple : triple[0], buyingDecisions)))
            participantsCount = len(interestedParticipants) 
            #initializing
            currentParticipantIndex = -1
            currentParticipant = None
            auctionWinner = None
            propertySite = None
            

            while True:

                participationCount = len(interestedParticipants) 
        
                if participationCount < 2:
                    break

                currentParticipantIndex = currentParticipantIndex % participationCount
                currentParticipant = interestedParticipants[currentParticipantIndex]
                
                # initization
                currentBid = None
                propertyId = None

                if self.state.getCash(currentParticipant) > highestBid:
                    # Assuming a auction decison API
                    # set something and call some predefined state
                    # set phase index and payload
                    (currentBid,propertyId) = self.runPlayerOnState(currentParticipant)
            
                if currentBid and currentBid > highestBid:
                    highestBid = currentBid
                    propertySite = propertyId
                    auctionWinner = currentParticipant
                    currentParticipantIndex +=1 
                else:
                    interestedParticipants.remove(currentParticipant)
            
            buyingDecisions = updateBuyingDecisions(buyingDecisions,auctionWinner,propertySite)
            constructionsRemaining -= 1

            # update cash and property 
            updateWinnerCash(auctionWinner, highestBid)
            updateWinnerProperty(auctionedProperty)

    
    """
    (Q: Will there need to be a BSTM if the player receives money?)
    Phase Properties:
    Is the property owned?
    If unowned, there are 3 sequential sub-phases: BSTM,Buying,Auction. Which one are you in?
    If owned, 2 sub-phases: BSTM,rent. Note: BSTM here for opponent must be applied after the turn.
    If cards, draw top card,do effect, return it to bottom of the deck.
    If Go To Jail, send to jail. Immediately end the turn.
    If currently in Jail, 3 ways to get out.
    """

    """
    Incoming action format:
    ("R",) : represents rolling to get out
    ("P",) : represents paying $50 to get out (BSMT should follow)
    ("C", propertyNumber) : represents using a get out of jail card, 
    but in case someone has both, needs to specify which one they are using. 
    In general, should always specify the number (either 28 or 29)
    Return values are 2 boolean values:
    1. Whether the player is out of jail.
    2. Whether there was a dice throw while handling jail state.
    """
    def handle_in_jail_state(self,action):
        currentPlayerId = self.state.getCurrentPlayerId()
        
        if action=="R" or action=="P":
            action = (action,)
        
        if (isinstance(action, tuple) or isinstance(action, list)) and len(action)>0:
            if action[0] == 'P':
                playerCash = self.state.getCash(currentPlayerId)
                #TODO: The player may not have enough money here. Is this the correct way to implement this?
                if playerCash>=50:
                    self.state.setCash(currentPlayerId,playerCash-50)
                else:
                    self.state.addDebtToBank(currentPlayerId,50)
                self.state.setPosition(currentPlayerId,self.JUST_VISTING)
                
                self.state.resetJailCounter(currentPlayerId)
                return [True,False]
            
            elif action[0] == 'C':
                #Check if the player has the mentioned property card.
                if (len(action)>1) & (action[1] in [self.CHANCE_GET_OUT_OF_JAIL_FREE,self.COMMUNITY_GET_OUT_OF_JAIL_FREE]):
                    
                    if self.state.isPropertyOwned(action[1]) and self.state.rightOwner(currentPlayerId,action[1]):
                        if action[1] == self.COMMUNITY_GET_OUT_OF_JAIL_FREE:
                            self.chest.deck.append(constants.communityChestCards[4])
                        elif action[1] == self.CHANCE_GET_OUT_OF_JAIL_FREE:
                            self.chance.deck.append(constants.chanceCards[7])
                        
                        self.state.setPropertyUnowned(action[1])
                        self.state.setPosition(currentPlayerId,self.JUST_VISTING)
                        self.state.resetJailCounter(currentPlayerId)
                        return [True,False]
        
        """If both the above method fail for some reason, we default to dice roll."""
        diceThrow = None
        if (self.diceThrows is not None) and len(self.diceThrows)>0:
            diceThrow = self.diceThrows.pop(0)
        self.dice.roll(dice=diceThrow)
        if self.dice.double:
            #Player can go out
            #Need to ensure that there is no second turn for the player in this turn.
            self.dice.double = False
            self.state.setPosition(currentPlayerId,self.JUST_VISTING)
            self.state.resetJailCounter(currentPlayerId)
            return [True,True]
        
        self.state.incrementJailCounter(currentPlayerId)
        if self.state.getJailCounter(currentPlayerId)==3:
            playerCash = self.state.getCash(currentPlayerId)
            #The player has to pay $50 and get out. 
            #This is added as debt so that the player has the opportunity to resolve it.
            self.state.addDebtToBank(currentPlayerId,50)
            self.state.setPosition(currentPlayerId,self.JUST_VISTING)
            self.state.resetJailCounter(currentPlayerId)

            log("jail","Agent "+str(currentPlayerId)+" has been in jail for 3 turns. Forcing him to pay $50 to get out.")
            return [True,True]
        return [False,True]
    
    """
    Returns 2 booleans 
    First is True if not in jail or no longer in jail
    Second is True if dice has already been thrown for the current turn while determining if the player should be let out or remain in jail
    """
    @inlineCallbacks
    def handle_jail(self):
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        if playerPosition != self.JAIL:
            return [True,False]
        
        #InJail
        self.state.setPhase(Phase.JAIL)
        self.state.setPhasePayload(None)
        action = yield self.runPlayerOnStateWithTimeout(currentPlayerId,"JAIL")
        result = self.handle_in_jail_state(action)
        
        phasePayload = [result[0]]
        self.state.setPhasePayload(phasePayload)
        
        #The player needs to know if he is still in jail or not.
        yield self.broadcastState()
        return result
    
    def send_player_to_jail(self):
        #Disable double
        self.dice.double = False
        
        currentPlayerId = self.state.getCurrentPlayerId()
        log("jail","Agent "+str(currentPlayerId)+" has been sent to jail")
        self.state.setPosition(currentPlayerId,self.JAIL)
        self.state.setPhase(Phase.JAIL)
        self.state.setPhasePayload(None)
    
    """
    Dice Roll Function
    1. Rolls the dice, checks for all the dice events.
    2. Then moves the player to new position and finds out what the effect of the position is.
    """
    def dice_roll(self,diceThrown):
        
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        playerCash = self.state.getCash(currentPlayerId)
        
        if not diceThrown:
            diceThrow = None
            if (self.diceThrows is not None) and len(self.diceThrows)>0:
                diceThrow = self.diceThrows.pop(0)
            self.dice.roll(dice=diceThrow)
        
        if self.dice.double_counter == 3:
            self.send_player_to_jail()
            return False
            #End current player's turn here
            #Should there be a GoToJail state to let the player know?
        else:
            #Update player position
            playerPosition += (self.dice.die_1 + self.dice.die_2)
            
            #Passing Go
            if playerPosition>=self.BOARD_SIZE:
                playerPosition = playerPosition % self.BOARD_SIZE
                playerCash += self.PASSING_GO_MONEY
            
            self.state.setCash(currentPlayerId,playerCash)
            self.state.setPosition(currentPlayerId,playerPosition)
            return True
    
    def isProperty(self,position):
        propertyClass = constants.board[position]['class']
        return (propertyClass == 'Street') or (propertyClass == 'Railroad') or (propertyClass == 'Utility')
    
    """
    Performed after dice is rolled and the player is moved to a new position.
    Determines the effect of the position and action required from the player.
    """     
    @inlineCallbacks
    def determine_position_effect(self):
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        playerCash = self.state.getCash(currentPlayerId)
        turn_number = self.state.getTurn()
        
        isProperty = self.isProperty(playerPosition)
        
        if isProperty:
            output = self.handle_property()
            if 'phase' in output:
                self.state.setPhase(output['phase'])
            if 'phase_properties' in output:
                self.state.setPhasePayload(output['phase_properties'])
            if 'debt' in output:
                self.state.setDebtToPlayer(currentPlayerId,output['debt'][0],output['debt'][1])
            
            if self.state.getPhase()==Phase.BUYING:
                action = yield self.runPlayerOnStateWithTimeout(currentPlayerId,"BUY")
                action = self.typecast(action, bool, False)
                if not action:
                    self.state.setPhase(Phase.AUCTION)
            
        elif constants.board[playerPosition]['class'] == 'Chance':
            #Chance
            card = self.chance.draw_card()
            
            log("cards","Chance card \""+str(card['content'])+"\" has been drawn")
            
            #ReceiveState
            phasePayload = card['id']
            self.state.setPhase(Phase.CHANCE_CARD)
            self.state.setPhasePayload(phasePayload)
            
            yield self.broadcastState()
            self.state.setPhase(Phase.NO_ACTION)
            self.state.setPhasePayload(None)
            self.handle_cards_pre_turn(card,'Chance')
            
        elif constants.board[playerPosition]['class'] == 'Chest':
            #Community
            card = self.chest.draw_card()
            
            log("cards","Community Chest card \""+str(card['content'])+"\" has been drawn")
            
            #ReceiveState
            phasePayload = card['id']
            self.state.setPhase(Phase.COMMUNITY_CHEST_CARD)
            self.state.setPhasePayload(phasePayload)
            
            yield self.broadcastState()
            self.state.setPhase(Phase.NO_ACTION)
            self.state.setPhasePayload(None)
            self.handle_cards_pre_turn(card,'Chest')
           
        elif constants.board[playerPosition]['class'] == 'Tax':
            #Tax
            cash = constants.board[playerPosition]['tax']
            self.state.setPhase(Phase.PAYMENT)
            self.state.setPhasePayload(None)
            self.state.addDebtToBank(currentPlayerId,cash)
        
        elif constants.board[playerPosition]['class'] == 'GoToJail':
            self.send_player_to_jail()
        
        elif constants.board[playerPosition]['class'] == 'Idle':
            #Represents Go,Jail(Visiting),Free Parking
            pass

    """
    Given that the current space is a property, determine what is to be done here.
    This method can only be called for the current player during any given turn.
    Hence only returns a 2 size tuple for debt.
    """
    def handle_property(self):
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        playerCash = self.state.getCash(currentPlayerId)
        isPropertyOwned = self.state.isPropertyOwned(playerPosition)
        ownerId = self.state.getPropertyOwner(playerPosition)
        
        output = {}
        if not isPropertyOwned:
            #Unowned
            output['phase'] = Phase.BUYING
            output['phase_properties'] = playerPosition
        elif ownerId!=currentPlayerId:
            space = constants.board[playerPosition]
            monopolies = space['monopoly_group_elements']
            counter = 1
            for monopoly in monopolies:
                if self.state.rightOwner(ownerId,monopoly):
                    counter += 1
            rent = space['rent']
            if (space['class'] == 'Street'):
                if (counter==len(monopolies)+1):
                    rent = rent * 2
                
                houseCount = self.state.getNumberOfHouses(playerPosition)
                if houseCount==1:
                    rent = space['rent_house_1']
                elif houseCount==2:
                    rent = space['rent_house_2']
                elif houseCount==3:
                    rent = space['rent_house_3']
                elif houseCount==4:
                    rent = space['rent_house_4']
                elif houseCount==5:
                    rent = space['rent_hotel']  
                
            elif (space['class'] == 'Railroad'):
                if counter == 2:
                    rent = 50
                if counter == 3:
                    rent = 100
                if counter == 4:
                    rent = 200
            elif (space['class'] == 'Utility'):
                if (counter==len(monopolies)+1):
                    rent = 10
                rent = rent * (self.dice.die_1 + self.dice.die_2)
            
            output['phase'] = Phase.PAYMENT
            output['phase_properties'] = playerPosition
            output['debt'] = (ownerId,rent)
        else:
            #When the property is owned by us
            pass
        
        return output

    """Method handles various events for Chance and Community cards"""
    @inlineCallbacks
    def handle_cards_pre_turn(self,card,deck):
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        playerCash = self.state.getCash(currentPlayerId)
        phaseNumber = self.state.getPhase()
        updateState = False
        
        phasePayload = None
        
        if card['type'] == 1:
            #-ve represents you need to pay
            if card['money']<0:
                phaseNumber = Phase.PAYMENT
                self.state.addDebtToBank(currentPlayerId,abs(card['money']))
            else:
                playerCash += abs(card['money'])

        elif card['type'] == 2:
            #-ve represents you need to pay
            phaseNumber = Phase.PAYMENT
            if card['money']<0:
                debtAmount = abs(card['money'])
                for playerId in self.PLAY_ORDER:
                    if playerId!=currentPlayerId and not self.state.hasPlayerLost(playerId):
                        self.state.setDebtToPlayer(currentPlayerId,playerId,debtAmount)
            else:
                debtAmount = abs(card['money'])
                for playerId in self.PLAY_ORDER:
                    if playerId!=currentPlayerId and not self.state.hasPlayerLost(playerId):
                        self.state.setDebtToPlayer(playerId,currentPlayerId,debtAmount)
            
        elif card['type'] == 3:
            if card['position'] == self.JAIL:
                #sending the player to jail
                playerPosition = self.JAIL
                self.send_player_to_jail()
            else:
                if (card['position'] - 1) < playerPosition:
                    #Passes Go
                    playerCash += self.PASSING_GO_MONEY
                playerPosition = card['position'] - 1
                updateState = True
                
        elif card['type'] == 4:
            """Get out of Jail free"""
            if deck == 'Chest':
                propertyValue = self.COMMUNITY_GET_OUT_OF_JAIL_FREE
            else:
                propertyValue = self.CHANCE_GET_OUT_OF_JAIL_FREE
            
            self.state.setPropertyOwner(propertyValue,currentPlayerId)
        
        elif card['type'] == 5:
            n_houses = 0
            n_hotels = 0
            for propertyId in range(self.BOARD_SIZE):
                if self.state.rightOwner(currentPlayerId,propertyId):
                    housesCount = self.state.getNumberOfHouses(propertyId)
                    if housesCount==5:
                        n_hotels+=1
                    else:
                        n_houses+=housesCount

            debtAmount = abs(card['money'])*n_houses + abs(card['money2'])*n_hotels
            if debtAmount > 0:
                phaseNumber = Phase.PAYMENT
                self.state.addDebtToBank(currentPlayerId,debtAmount)
        
        elif card['type'] == 6:
            #Advance to nearest railroad. Pay 2x amount if owned
            if (playerPosition < 5) or (playerPosition>=35):
                if (playerPosition>=35):
                    #Passes Go
                    playerCash += self.PASSING_GO_MONEY
                playerPosition = 5
            elif (playerPosition < 15) and (playerPosition>=5):
                playerPosition = 15
            elif (playerPosition < 25) and (playerPosition>=15):
                playerPosition = 25
            elif (playerPosition < 35) and (playerPosition>=25):
                playerPosition = 35
            
            self.state.setPosition(currentPlayerId,playerPosition)
            output = self.handle_property()
            if 'phase' in output:
                phaseNumber = output['phase']
            if 'phase_properties' in output:
                phasePayload = output['phase_properties']
            if 'debt' in output:
                #We need to double rent if the player landed on opponent's property.
                self.state.setDebtToPlayer(currentPlayerId,output['debt'][0],output['debt'][1]*2)
        
        elif card['type'] == 7:
            #Advance to nearest utility. Pay 10x dice roll if owned
            if (playerPosition < 12) or (playerPosition>=28):
                if (playerPosition>=28):
                    #Passes Go
                    playerCash += self.PASSING_GO_MONEY
                playerPosition = 12
            elif (playerPosition < 28) and (playerPosition>=12):
                playerPosition = 28
            
            ownerId = self.state.getPropertyOwner(playerPosition)
            if not self.state.isPropertyOwned(playerPosition):
                #Unowned
                phaseNumber = Phase.BUYING
                phasePayload = playerPosition
            elif ownerId!=currentPlayerId:
                #Check if owned by opponent
                diceThrow = None
                if (self.diceThrows is not None) and len(self.diceThrows)>0:
                    diceThrow = self.diceThrows.pop(0)
                self.dice.roll(ignore=True,dice=diceThrow)
                
                phaseNumber = Phase.PAYMENT
                self.state.setDebtToPlayer(currentPlayerId,ownerId,10 * (self.dice.die_1 + self.dice.die_2))
        
        elif card['type'] == 8:
            #Go back 3 spaces
            playerPosition -= 3 
            updateState = True
        else:
            logger.info('Invalid card type {type}...'.format(type=card['type']))
        
        self.state.setPosition(currentPlayerId,playerPosition)
        self.state.setCash(currentPlayerId,playerCash)
        self.state.setPhase(phaseNumber)
        self.state.setPhasePayload(phasePayload)
        
        if phaseNumber==Phase.BUYING:
                action = yield self.runPlayerOnStateWithTimeout(currentPlayerId,"BUY")
                action = self.typecast(action, bool, False)
                if not action:
                    self.state.setPhase(Phase.AUCTION)
        
        # make further calls
        if updateState:
            yield self.determine_position_effect()
    
    """
    Handle the action response from the Agent for buying an unowned property
    Only called for the currentPlayer during his turn.
    """ 
    def handle_buy_property(self):
        currentPlayerId = self.state.getCurrentPlayerId()
        playerPosition = self.state.getPosition(currentPlayerId)
        playerCash = self.state.getCash(currentPlayerId)
        price = constants.board[playerPosition]['price']
        
        if playerCash>=price:
            self.state.setPropertyOwner(playerPosition,currentPlayerId)
            self.state.setCash(currentPlayerId,playerCash-price)
            log('buy',"Agent "+str(currentPlayerId)+" has bought "+constants.board[playerPosition]['name'])
            #Clearing the payload as the buying has been completed
            self.state.setPhasePayload(None)
            return True
        
        #This would indicate going to Auction
        return False
    
    """
    Handling payments the player has to make to the bank/opponent
    Could be invoked for either player during any given turn.
    Returns 2 boolean list - True if the player was able to pay off his debt
    """
    def handle_payment(self):
        for playerId in self.PLAY_ORDER:
            if not self.state.hasPlayerLost(playerId):
                self.state.clearDebt(playerId)
    
    """Function calls the relevant method of the Agent"""
    @inlineCallbacks
    def turn_effect(self):
        currentPlayerId = self.state.getCurrentPlayerId()
        phase = self.state.getPhase()
        phasePayload = self.state.getPhasePayload()
        if phase == Phase.BUYING:
            self.handle_buy_property()
        elif phase == Phase.AUCTION:
            auctionedProperty = phasePayload
            turn_effect = yield self.handle_auction(auctionedProperty)
            return turn_effect
    """
    On final winner calculation, following are considered:
    Player's cash,
    Property value as on the title card,
    House and Hotel purchase value,
    Mortgaged properties at half price.
    """
    def final_winning_condition(self):
        agentCash = {}
        agentPropertyWorth = {}
        
        for playerId in self.PLAY_ORDER:
            agentCash[playerId] = self.state.getCash(playerId)
            agentPropertyWorth[playerId] = 0
        
        for propertyId in range(40):
            #In 0 to 39 board position range
            isPropertyOwned = self.state.isPropertyOwned(propertyId)
            ownerId = self.state.getPropertyOwner(propertyId)
            houses = self.state.getNumberOfHouses(propertyId)
            mortgaged = self.state.isPropertyMortgaged(propertyId)
            
            price = constants.board[propertyId]['price']
            build_cost = constants.board[propertyId]['build_cost']
            
            if isPropertyOwned:
                if mortgaged:
                    agentPropertyWorth[ownerId] += int(price/2)
                else:
                    agentPropertyWorth[ownerId] += (price+build_cost*houses)
        
        for propertyId in [self.CHANCE_GET_OUT_OF_JAIL_FREE,self.COMMUNITY_GET_OUT_OF_JAIL_FREE]:
            isPropertyOwned = self.state.isPropertyOwned(propertyId)
            ownerId = self.state.getPropertyOwner(propertyId)
            if isPropertyOwned:
                agentPropertyWorth[ownerId] += 50
        
        #Gives the list of players sorted in descending order.
        #Also takes into consideration if player lost earlier in the game.
        #for playerId in self.PLAY_ORDER:
        #    log("win_condition","Agent "+str(playerId)+" Cash: "+str(agentCash[playerId]))
        #    log("win_condition","Agent "+str(playerId)+" Property Value: "+str(agentPropertyWorth[playerId]))
        #def winnerSorting(playerId):
        #    if self.state.getTurnOfLoss(playerId)==-1:
        #        return self.TOTAL_NO_OF_TURNS+agentCash[playerId]+agentPropertyWorth[playerId]
        #    else:
        #        return self.state.getTurnOfLoss(playerId)
        #SHOULD CREATE A COPY OF self.PLAY_ORDER before sorting it here
        #return sorted(self.PLAY_ORDER,key=winnerSorting,reverse=True)
        
        #Using an array here to handle ties
        winners = []
        highestAssets = 0
        for playerId in self.PLAY_ORDER:
            turn_of_loss = self.state.getTurnOfLoss(playerId)
            if turn_of_loss==-1:
                log("win_condition","Agent "+str(playerId)+" Cash: "+str(agentCash[playerId]))
                log("win_condition","Agent "+str(playerId)+" Property Value: "+str(agentPropertyWorth[playerId]))
                playerAssets = agentCash[playerId]+agentPropertyWorth[playerId]
                if playerAssets > highestAssets:
                    winners = [playerId]
                    highestAssets = playerAssets
                elif playerAssets == highestAssets:
                    winners.append(playerId)
            else:
                log("win_condition","Agent "+str(playerId)+" had lost in the turn: "+str(turn_of_loss))
        
        return winners
    
    def initialize_debug_state(self,diceThrows,chanceCards,communityCards):
        if isinstance(diceThrows, list) and len(diceThrows)>0:
            self.diceThrows = diceThrows
        else:
            self.diceThrows = diceThrows
            
        if isinstance(chanceCards, list) and len(chanceCards)>0:
            self.chance.reinit(constants.chanceCards,chanceCards)
        
        if isinstance(communityCards, list) and len(communityCards)>0:
            self.chest.reinit(constants.communityChestCards,communityCards)
    
    @inlineCallbacks
    def broadcastState(self):
        for playerId in self.PLAY_ORDER:
            yield self.runPlayerOnStateWithTimeout(playerId,"INFO")
    
    """
    Function to be called to start the game.
    Expects agents to be in the order of play.
    """
    @inlineCallbacks
    def runGame(self,agents,diceThrows=None,chanceCards=None,communityCards=None):
        
        self.stateHistory = []
        self.mortgagedDuringTrade = []

        self.chest = Cards(constants.communityChestCards)
        self.chance = Cards(constants.chanceCards)
        
        #Stores the list of agents which are competing in the current game in the order of play.
        self.agents = agents
        self.PLAY_ORDER = agents #Stores the id's of all the players in the order of play
        self.TOTAL_NO_OF_PLAYERS = len(self.agents)
        
        self.dice = Dice()
        self.state =  State(self.PLAY_ORDER)
        winner = None
        
        #Setting an initial state. Used during testing.
        #if isinstance(state,list) and len(state)==6:
        #   self.state = state
        
        self.initialize_debug_state(diceThrows,chanceCards,communityCards)
        
        while (self.state.getTurn() < self.TOTAL_NO_OF_TURNS) and ( (self.diceThrows is None) or (len(self.diceThrows)>0) ):
            
            self.state.updateTurn()
            
            playerId = self.state.getCurrentPlayerId()
            if self.state.hasPlayerLost(playerId):
                continue
            
            self.dice.reset()
            
            log("turn","Turn "+str(self.state.getTurn())+" start")
            log("state","State at the start of the turn:")
            log("state",self.state)
            
            while ( (self.diceThrows is None) or (len(self.diceThrows)>0) ):
                
                self.state.setPhase(Phase.NO_ACTION)
                self.state.setPhasePayload(None)    
                
                [outOfJail,diceThrown] = yield self.handle_jail()
                if self.state.hasPlayerLost(playerId):
                    break
                
                if outOfJail:
                    """rolls dice, moves the player and determines what happens on the space he has fallen on."""
                    notInJail = self.dice_roll(diceThrown)
                    if self.state.hasPlayerLost(playerId):
                        break
                    
                    if notInJail:
                        yield self.determine_position_effect()
                        if self.state.hasPlayerLost(playerId):
                            break
                        
                        log("state","State after moving the player and updating state with effect of the position:")
                        log("state",self.state)
                        
                        """BSMT"""
                        self.mortgagedDuringTrade = []
                        previousPhase = self.state.getPhase()
                        previousPhasePayload = self.state.getPhasePayload()
                        self.state.setPhase(Phase.TRADE)
                        self.state.setPhasePayload(None)
                        self.conductBSM()
                        if self.state.hasPlayerLost(playerId):
                            break
                        yield self.conductTrade()
                        self.state.setPhase(previousPhase)
                        self.conductBSM()
                        if self.state.hasPlayerLost(playerId):
                            break
                        self.state.setPhasePayload(previousPhasePayload)
                        
                        """State now contain info about the position the player landed on"""
                        """Performing the actual effect of the current position"""
                        yield self.turn_effect()
                        if self.state.hasPlayerLost(playerId):
                            break
                        
                        self.handle_payment()
                        if self.state.hasPlayerLost(playerId):
                            break
                
                log("state","State at the end of the turn:")
                log("state",self.state)
                
                if (not self.dice.double):
                    break
                else:
                    log("dice","Rolled Doubles. Play again.")
            
            log("turn","Turn "+str(self.state.getTurn())+" end")
            
            """Update the turn counter"""
            lossCount = 0
            for agentId in self.PLAY_ORDER:
                if self.state.hasPlayerLost(agentId): lossCount+=1
            if lossCount>=self.TOTAL_NO_OF_PLAYERS-1:
                #Only one player left. Winner has been decided.
                log("win","Only one player left.")
                break
        
        #TODO:
        #Storing the state_history to log file
        #f = open("state_history.log", "w")
        #for history in self.stateHistory:
        #   f.write(str(history)+",\n")
        
        """Determine the winner"""
        resultsArray = self.final_winning_condition()
        if len(resultsArray)>1:
             log("win","Agents "+str(resultsArray)+" won the Game.")
        else:
             log("win","Agent "+str(resultsArray[0])+" won the Game.")

        self.state.setPhasePayload(None)
        finalState = self.state.toJson()
        #finalState = self.state
        return [resultsArray,finalState]
    
    """
    This function is called whenever adjudicator needs to communicate with the agent
    The function to called on the agent is determined by reading the state.
    All threading and signal based logic must go in here
    """
    """
        Not sure the timning related thing works now; lets keep it on hold
    """
    # @timeout_decorator.timeout(3000, timeout_exception=TimeoutError)
    # def runPlayerOnStateWithTimeout(self, playerId,callType):
    #     try:
    #         return self.runPlayerOnState(playerId,callType)
    #     except TimeoutError:
    #         print("Agent Timed Out")
    #         """Change the return value here to ensure agent loses"""
    #         self.state.markPlayerLost(playerId,Reason.TIMEOUT)
    #         return None

    @inlineCallbacks
    def runPlayerOnStateWithTimeout(self,playerId,callType):
        # player = self.getPlayer(playerId)
        action = None
        stateToBeSent = self.state.toJson()
        # stateToBeSent = self.state
        
        phaseProcedureMapping = {
            "BSM" : "monopoly.agent{}.bsm",
            "BUY" : "monopoly.agent{}.buy",
            "AUCTION" : "monopoly.agent{}.auction",
            "JAIL" : "monopoly.agent{}.jail",
            "TRADE" : "monopoly.agent{}.trade",
            "INFO" : "monopoly.agent{}.receivestate",
            "RESPOND_TRADE" : "monopoly.agent{}.respondtrade"
        }

        procedure = phaseProcedureMapping[callType].format(str(playerId))
       
        try:
            action = yield self.call(procedure, stateToBeSent)
        except:
            print(procedure)
        
        return action


if __name__ == '__main__':
    import six
    url = environ.get("CBURL", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(Component)

# for testing purposes only
#adjudicator = Adjudicator()
#adjudicator.runGame(agentOne, agentTwo)