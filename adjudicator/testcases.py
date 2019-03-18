from adjudicator import Adjudicator
from state import Property

PLAYER_ID_INDEX = 0
PLAYER_TURN_INDEX = 1
PROPERTY_STATUS_INDEX = 2
PLAYER_POSITION_INDEX = 3
PLAYER_CASH_INDEX = 4
PLAYER_BANKRUPT_INDEX = 5
PHASE_NUMBER_INDEX = 6
PHASE_PAYLOAD_INDEX = 7
DEBT_INDEX = 6

def compare_states(state,expected_output):
	playerIds = state.players
	passCounter = 0
	if 'turn' in expected_output:
		if (state.getTurn() == expected_output['turn']):
			passCounter+=1
		else:
			print("Turn number doesn't match")
	
	if 'cash' in expected_output:
		passed = True
		for playerId in playerIds:
			if not state.getCash(playerId) == expected_output['cash'][playerId]:
				passed = False
				break
		if passed:
			passCounter+=1
		else:
			print("cash doesn't match")
	
	if 'position' in expected_output:
		passed = True
		for playerId in playerIds:
			if not state.getPosition(playerId) == expected_output['position'][playerId]:
				passed = False
				break
		if passed:
			passCounter+=1
		else:
			print("position number doesn't match")
			
	if 'properties' in expected_output:
		passed = True
		for id,attributes in expected_output['properties']:
			if not attributes.houses == state.getNumberOfHouses(id):
				passed = False
				break
			if not attributes.mortgaged == state.isPropertyMortgaged(id):
				passed = False
				break
			if not attributes.owned == state.isPropertyOwned(id):
				passed = False
				break
			if not attributes.ownerId == state.getPropertyOwner(id):
				passed = False
				break
			
		if passed:
			passCounter+=1
		else:
			print("Properties don't match")
			
	if passCounter >= len(expected_output):
		return True
	else:
		return False

def testcase_auction(adjudicator):
	print("Test Case: Description:")
	print("AgentTwo will fall on Vermont Avenue(Position 8) and will decide to auction it.")
	print("AgentTwo will bid $175.5 and AgentOne $160")
	print("The auction would be won by AgentTwo who will only pay 175")
	
	class AgentOne:
		def __init__(self, id):
			self.id = id
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return False
		
		def auctionProperty(self, state):
			return 160
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return False
	
		def auctionProperty(self, state):
			return 175.5
		
		def receiveState(self, state):
			pass
	
	class AgentThree:
		def __init__(self, id):
			self.id = id
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return False
	
		def auctionProperty(self, state):
			return 170
		
		def receiveState(self, state):
			pass
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	agentThree = AgentThree("3")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo,agentThree],[[3,5]],None,None)
	
	expected_output = {
		"cash": {"1": 1500, "2": 1500-175, "3": 1500},
		"position": {"1": 8, "2": 0,"3": 0},
		"properties":[( 8,Property(houses=0,mortgaged=False,owned=True,ownerId="2") )]
	}
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	print("")
	
	return result

def testcase_payment(adjudicator):
	print("Test Case: Description:")
	print("AgentTwo will fall on Income Tax(Position 4) and has to pay the bank $200.")
	
	class AgentOne:
		def __init__(self, id):
			self.id = id
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return False
		
		def auctionProperty(self, state):
			return 160
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return False
	
		def auctionProperty(self, state):
			return 170
		
		def receiveState(self, state):
			pass
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[3,1]],None,None)
	
	expected_output = {
		"cash": {"1": 1500-200, "2": 1500},
		"position": {"1": 4, "2": 0}
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else: 
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_buying_houses(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				return ("BHS", [(6,1),(8,2),(9,1)])
			else:
				return None
			
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None	
		
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Buying of houses")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-200, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[( 6,Property(1,False,True,"1") ),( 8,Property(2,False,True,"1") ),
					( 9,Property(1,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result
	
def testcase_selling_houses(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			orientalHouses = state.getNumberOfHouses(6)
			vermontHouses = state.getNumberOfHouses(8)
			connecticutHouses = state.getNumberOfHouses(9)
			
			if (orientalHouses == 1) and (vermontHouses == 2) and (connecticutHouses == 1):
				return ("S", [(6,1,False),(8,1,False)])
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				return ("BHS", [(6,1),(8,2),(9,1)])
			
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Selling of houses")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-200+50, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[( 6,Property(0,False,True,"1") ),( 8,Property(1,False,True,"1") ),
					( 9,Property(1,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_trade(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
		def respondTrade(self,state):
			return True
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			self.trade_status = None
		
		def getBSMTDecision(self, state):
			return None	
		
		def getTradeDecision(self, state):
			isConnecticutOwned = state.isPropertyOwned(9)
			connecticutOwnerId = state.getPropertyOwner(9)
			
			if isConnecticutOwned and connecticutOwnerId!=self.id and (self.trade_status==None):
				return (connecticutOwnerId,50.5,[19],0,[9])
			
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			phase = state.getPhase()
			if phase == 1:#Trade Offer Phase
				(self.trade_status,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest) = state.getPhasePayload()
	
	print("\nTest Case: Trade")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3],[2,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-160+50, "2": 1500-140-200-150-50},
		"position": {"1": 14, "2": 28},
		"properties":[( 6,Property(0,False,True,"1") ),( 8,Property(0,False,True,"1") ),
					( 9,Property(0,False,True,"2") ),( 11,Property(0,False,True,"2") ),
					( 14,Property(0,False,True,"1") ),( 19,Property(0,False,True,"1") ),
					( 28,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_buying_houses_invalid_1(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				if self.erronous_bstm_counter < 1:
					self.erronous_bstm_counter += 1
					return ("BHS", [(6,1),(8,3),(9,1)]) # Uneven buying of houses
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			stcharles = state.getPropertyOwner(11)
			if (stcharles == self.id) and (self.erronous_bstm_counter < 1):
				self.erronous_bstm_counter += 1
				return ("BHS", [(11,1)]) #Buying houses without completing monopoly
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Trying to buy houses without completing monopoly")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[ ( 6,Property(0,False,True,"1") ),( 8,Property(0,False,True,"1") ),
					( 9,Property(0,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") ) ]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_buying_houses_invalid_2(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				return ("BHS", [(6,4),(8,5),(9,4)]) #Trying to buy houses and a hotel together
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Trying to buy an invalid number of houses in a completed monopoly")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[ ( 6,Property(0,False,True,"1") ),( 8,Property(0,False,True,"1") ),
					( 9,Property(0,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") ) ]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_mortgaging_unmortgaging(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			isOrientalMortgaged = state.isPropertyMortgaged(6)
			vermont = state.getPropertyOwner(8)
			isVermontMortgaged = state.isPropertyMortgaged(8)
			connecticut = state.getPropertyOwner(9)
			isConnecticutMortgaged = state.isPropertyMortgaged(9)
			
			if (oriental == self.id) and not isOrientalMortgaged and (vermont == self.id) and not isVermontMortgaged and (connecticut == self.id) and not isConnecticutMortgaged:
				return ("M", [6,8,9])
			elif isOrientalMortgaged:
				return ("M", [6])
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Unmortgaging a property")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120+50+50+60-50-5, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[ ( 6,Property(0,False,True,"1") ),( 8,Property(0,True,True,"1") ),
					( 9,Property(0,True,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") ) ]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_invalid_mortgaging(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			newyork = state.getPropertyOwner(19)
			waterworks = state.getPropertyOwner(28)
			
			if (newyork == -1):
				return ("M", [19]) #Owned by opponent
			elif (waterworks == -1):
				return ("M", [29]) #Unowned Property
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Trying to mortgage opponent's property and an unowned property")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[ ( 6,Property(0,False,True,"1") ),( 8,Property(0,False,True,"1") ),
					( 9,Property(0,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") ) ]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_auction_for_invalid_action(adjudicator):
	print("\nTest Description:")
	print("AgentOne will fall on Vermont Avenue(Position 8) and will decide to auction it.")
	print("AgentTwo will bid $170 and AgentOne will pass Junk Value")
	print("The auction would be won by AgentTwo")

	class AgentOne:
		def __init__(self, id):
			self.id = id

		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return False

		def auctionProperty(self, state):
			return "Junk Value"

		def receiveState(self, state):
			pass

	class AgentTwo:
		def __init__(self, id):
			self.id = id

		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return False

		def auctionProperty(self, state):
			return 170

		def receiveState(self, state):
			pass

	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	adjudicator.runGame([agentOne,agentTwo],[[3, 5]], None, None)

	final_state = adjudicator.state
	
	expected_output = {
		"cash": {"1": 1500, "2": 1500-170},
		"position": {"1": 8, "2": 0},
		"properties":[ ( 8,Property(0,False,True,"2") ) ]
	}

	result = compare_states(final_state, expected_output)

	if result:
		print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)

	print("")

	return result

def testcase_trade_for_invalid_action(adjudicator):
	print("Test Description:")
	print("AgentOne falls on Oriental Avenue and buys it.")
	print("AgentTwo falls on St. Charles Avenue and buys it.")
	print("AgentOne will trade Oriental Avenue property for St. Charles Avenue and AgentTwo returns Junk Value")

	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0

		def getBSMTDecision(self, state):
			isOrientalOwned = state.isPropertyOwned(6)
			orientalOwnerId = state.getPropertyOwner(6)
			
			if isOrientalOwned and (orientalOwnerId != self.id) and self.erronous_bstm_counter == 0:
				self.erronous_bstm_counter = 1
				return (orientalOwnerId, 0, [6], 0, [11])
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return True

		def auctionProperty(self, state):
			return 160

		def receiveState(self, state):
			pass

		def respondTrade(self, state):
			return False

	class AgentTwo:
		def __init__(self, id):
			self.id = id

		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return True

		def auctionProperty(self, state):
			return 170

		def receiveState(self, state):
			pass

		def respondTrade(self, state):
			return "Junk Value"

	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1, 5], [5, 6]], None, [0])
	
	# Since the trade is unsuccessful here
	expected_output = {
		"properties":[ ( 6,Property(0,False,True,"1") ) ]
	}
	
	result = compare_states(final_state,expected_output)

	if result:
		print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)

	print("")

	return result

def testcase_buyproperty_for_invalid_action(adjudicator):
	print("Test Description:")
	print("AgentOne will fall on Vermont Avenue(Position 8) and will return an erroneous value. This should start an auction phase.")
	print("AgentTwo will bid $170 and AgentOne will bid $160")
	print("The auction would be won by AgentTwo")

	class AgentOne:
		def __init__(self, id):
			self.id = id

		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return "Junk Value"

		def auctionProperty(self, state):
			return 160

		def receiveState(self, state):
			pass

	class AgentTwo:
		def __init__(self, id):
			self.id = id

		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None

		def buyProperty(self, state):
			return False

		def auctionProperty(self, state):
			return 170

		def receiveState(self, state):
			pass
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	adjudicator.runGame([agentOne,agentTwo],[[3, 5]], None, None)

	final_state = adjudicator.state
	
	expected_output = {
		"cash": {"1": 1500, "2": 1500-170},
		"position": {"1": 8, "2": 0},
		"properties":[( 8,Property(0,False,True,"2") )]
	}

	result = compare_states(final_state, expected_output)

	if result:
		print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)

	return result

def testcase_buying_two_hotels(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bsm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			orientalHouses = state.getNumberOfHouses(6)
			vermontHouses = state.getNumberOfHouses(8)
			connecticutHouses = state.getNumberOfHouses(9)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				if orientalHouses==0 and vermontHouses==0 and connecticutHouses==0:
					return ("BHS", [(6,4),(8,4),(9,4)])
				elif orientalHouses==4 and vermontHouses==4 and connecticutHouses==4:
					return ("BHT",[6,8]) #Valid
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Buying hotels on two properties in a single monopoly")
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-14*50, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[( 6,Property(5,False,True,"1") ),( 8,Property(5,False,True,"1") ),
					( 9,Property(4,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_invalid_hotel(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bsm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			orientalHouses = state.getNumberOfHouses(6)
			vermontHouses = state.getNumberOfHouses(8)
			connecticutHouses = state.getNumberOfHouses(9)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id):
				if orientalHouses==0 and vermontHouses==0 and connecticutHouses==0:
					return ("BHS", [(6,4),(8,4),(9,3)])
				elif orientalHouses==4 and vermontHouses==4 and connecticutHouses==3:
					return ("BHT",[6,8]) #Valid
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Buying hotels without completing the monopoly")
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3]],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-11*50, "2": 1500-140-200-150},
		"position": {"1": 9, "2": 28},
		"properties":[( 6,Property(4,False,True,"1") ),( 8,Property(4,False,True,"1") ),
					( 9,Property(3,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 19,Property(0,False,True,"2") ),( 28,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testGettingOutOfJail(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
		def jailDecision(self,state):
			return ("P",)
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
	print("\nTest Case: AgentOne ends up in Jail by rolling 3 doubles in a row. He pays to get out in the next turn and moves to a certain position.")
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	dice = [(6, 6),(6, 6),(6, 6), (2, 3),(4,2)]
	
	[winner, final_state] = adjudicator.runGame([agentOne,agentTwo], dice, [], [])
	
	expected_output = {
		"cash": {"1": 1500-150-240-50-180, "2": 1500-200},
		"position": {"1": 16, "2": 5},
		"properties":[( 12,Property(0,False,True,"1") ),( 24,Property(0,False,True,"1") ),
					( 5,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_three_jails_a_day_keeps_the_lawyer_away(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			orientalHouses = state.getNumberOfHouses(6)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id) and orientalHouses==0:
				return ("BHS", [(6,4),(8,4),(9,4)])
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
		def jailDecision(self,state):
			return ("R",)
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Player stays in jail for 3 turns and has to pay and get out on the third turn.")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5], [5,6], [1,1],[5,4], [2,6], [5,4], [6,3], [3,3],[5,4], [5,4], [5,1], [5,3], [5,6], [4,3], [4,3], [5,3], [4,5]],None,[0,1])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-600-200-240-50-16, "2": 1500-140-200-150-350-150+16},
		"position": {"1": 19, "2": 20},
		"properties":[( 6,Property(4,False,True,"1") ),( 8,Property(4,False,True,"1") ),
					( 9,Property(4,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 12,Property(0,False,True,"2") ),( 15,Property(0,False,True,"1") ),
					( 19,Property(0,False,True,"2") ),( 24,Property(0,False,True,"1") ),
					( 28,Property(0,False,True,"2") ),( 37,Property(0,False,True,"2") ),
					( 5,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result and winner=="2": 
		print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_three_jails_a_day_keeps_the_lawyer_away_2(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			orientalHouses = state.getNumberOfHouses(6)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id) and orientalHouses==0:
				return ("BHS", [(6,4),(8,4),(9,4)])
			return None
			
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
		def jailDecision(self,state):
			return ("R",)
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Player stays in jail for 3 turns and has to pay and get out on the third turn. But he doesn't have enough and goes bankrupt.")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5], [5,6], [1,1],[5,4], [2,6], [5,4], [6,3], [3,3],[5,4], [5,4], [1,1],[1,1],[1,1], [5,3], [5,6], [4,3], [4,3], [5,3], [4,3]],None,[0,1])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-600-200-240-260-8+200-50, "2": 1500-140-200-150-350-150+8},
		"position": {"1": 17, "2": 20},
		"properties":[( 6,Property(4,False,True,"1") ),( 8,Property(4,False,True,"1") ),
					( 9,Property(4,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 12,Property(0,False,True,"2") ),( 15,Property(0,False,True,"1") ),
					( 19,Property(0,False,True,"2") ),( 24,Property(0,False,True,"1") ),
					( 26,Property(0,False,True,"1") ),( 28,Property(0,False,True,"2") ),
					( 37,Property(0,False,True,"2") ),( 5,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: 
		print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_buying_max_houses(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			oriental_houses = state.getNumberOfHouses(6)
			
			orange_0 = state.getPropertyOwner(16)
			orange_1 = state.getPropertyOwner(18)
			orange_2 = state.getPropertyOwner(19)
			orange_2_houses = state.getNumberOfHouses(19)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id) and oriental_houses==0:
				return ("BHS", [(6,4),(8,4),(9,4)])
			if (orange_0 == self.id) and (orange_1 == self.id) and (orange_2 == self.id) and orange_2_houses==0:
				return ("BHS", [(16,2),(18,1),(19,1)])
			if orange_2_houses==1 and self.erronous_bstm_counter==0:
				#This build operation would fail.Already reached 32 houses.
				self.erronous_bstm_counter+=1
				return ("BHS", [(19,1)])
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			propertyId = state.getPhasePayload()
			if propertyId == 39:
				return False
			return True
		
		def auctionProperty(self, state):
			return 8
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			pink_0 = state.getPropertyOwner(11)
			pink_1 = state.getPropertyOwner(13)
			pink_2 = state.getPropertyOwner(14)
			pink_0_houses = state.getNumberOfHouses(11)
			
			red_0 = state.getPropertyOwner(21)
			red_1 = state.getPropertyOwner(23)
			red_2 = state.getPropertyOwner(24)
			red_2_houses = state.getNumberOfHouses(24)
			
			cash = state.getCash("2")
			
			if (pink_0 == self.id) and (pink_1 == self.id) and (pink_2 == self.id) and pink_0_houses==0:
				return ("BHS", [(11,4),(13,4),(14,4)])
			if (red_0 == self.id) and (red_1 == self.id) and (red_2 == self.id) and red_2_houses==0 and cash>=600:
				return ("BHS", [(21,2),(23,1),(24,1)])
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return False
	
		def auctionProperty(self, state):
			propertyId = state.getPhasePayload()
			if propertyId==18:
				return 5
			return 10
		
		def receiveState(self, state):
			pass
		
		def jailDecision(self,state):
			return ("P",)
	
	print("\nTest Case: Trying to buy a house when all 32 houses have already been constructed")
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5], [5,6], [1,1],[5,4], [1,1],[5,5],[3,3], [5,4], [2,2],[5,5],[3,3], [3,4], [6,5], [1,2], [6,6],[5,4], [1,2], [5,4], [3,5], [4,3], [5,3]],[13,0],[0,1,7])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-600-180-200+200+200-8-400, "2": 1500-10-10-10-50-10-1200-10-50-10+200+200+100-600-10},
		"position": {"1": 8, "2": 18},
		"properties":[( 6,Property(4,False,True,"1") ),( 8,Property(4,False,True,"1") ),
					( 9,Property(4,False,True,"1") ),( 11,Property(4,False,True,"2") ),
					( 13,Property(4,False,True,"2") ),( 14,Property(4,False,True,"2") ),
					( 16,Property(2,False,True,"1") ),( 18,Property(1,False,True,"1") ),
					( 19,Property(1,False,True,"1") ),( 21,Property(2,False,True,"2") ),
					( 23,Property(1,False,True,"2") ),( 24,Property(1,False,True,"2") ),
					( 39,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_selling_hotel_aftermax(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			oriental_houses = state.getNumberOfHouses(6)
			
			orange_0 = state.getPropertyOwner(16)
			orange_1 = state.getPropertyOwner(18)
			orange_2 = state.getPropertyOwner(19)
			orange_2_houses = state.getNumberOfHouses(19)
			
			if (oriental == self.id) and (vermont == self.id) and (connecticut == self.id) and oriental_houses==0:
				return ("BHS", [(6,4),(8,4),(9,4)])
			if (orange_0 == self.id) and (orange_1 == self.id) and (orange_2 == self.id) and orange_2_houses==0:
				return ("BHS", [(16,2),(18,1),(19,1)])
			if oriental_houses==4:
				return ("BHT", [6])
			if orange_2_houses==1:
				return ("BHS", [(18,1),(19,2)])
			elif oriental==6:
				return ("S",[(6,0,True)]) # Selling Hotel on Oriental. Should fail.
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			propertyId = state.getPhasePayload()
			if propertyId == 39:
				return False
			return True
		
		def auctionProperty(self, state):
			return 8
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			
		def getBSMTDecision(self, state):
			pink_0 = state.getPropertyOwner(11)
			pink_1 = state.getPropertyOwner(13)
			pink_2 = state.getPropertyOwner(14)
			pink_0_houses = state.getNumberOfHouses(11)
			
			red_0 = state.getPropertyOwner(21)
			red_1 = state.getPropertyOwner(23)
			red_2 = state.getPropertyOwner(24)
			red_2_houses = state.getNumberOfHouses(24)
			cash = state.getCash("2")
			
			if (pink_0 == self.id) and (pink_1 == self.id) and (pink_2 == self.id) and pink_0_houses==0:
				return ("BHS", [(11,4),(13,4),(14,4)])
			if (red_0 == self.id) and (red_1 == self.id) and (red_2 == self.id) and red_2_houses==0 and cash>=600:
				return ("BHS", [(21,2),(23,1),(24,1)])
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return False
	
		def auctionProperty(self, state):
			propertyId = state.getPhasePayload()
			if propertyId==18:
				return 5
			return 10
		
		def receiveState(self, state):
			pass
		
		def jailDecision(self,state):
			return ("P",)
	
	print("\nTest Case: Trying to sell a hotel when more than 28 houses have already been constructed")
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5], [5,6], [1,1],[5,4], [1,1],[5,5],[3,3], [5,4], [2,2],[5,5],[3,3], [3,4], [6,5], [1,2], [6,6],[5,4], [1,2], [5,4], [3,5], [4,3], [3,4]],[13,0,15],[0,1,7])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-600-180-200+200+200-8-400-350+150, "2": 1500-10-10-10-50-1200-10-50-10-10+200+200+100-600-10},
		"position": {"1": 7, "2": 18},
		"properties":[( 6,Property(5,False,True,"1") ),( 8,Property(4,False,True,"1") ),
					( 9,Property(4,False,True,"1") ),( 11,Property(4,False,True,"2") ),
					( 13,Property(4,False,True,"2") ),( 14,Property(4,False,True,"2") ),
					( 16,Property(2,False,True,"1") ),( 18,Property(2,False,True,"1") ),
					( 19,Property(3,False,True,"1") ),( 21,Property(2,False,True,"2") ),
					( 23,Property(1,False,True,"2") ),( 24,Property(1,False,True,"2") ),
					( 39,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_trade_mortgage(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
		
		def getBSMTDecision(self, state):
			oriental = state.getPropertyOwner(6)
			vermont = state.getPropertyOwner(8)
			connecticut = state.getPropertyOwner(9)
			
			orange_2 = state.getPropertyOwner(19)
			orange_2_isMortgaged = state.isPropertyMortgaged(19)
			
			if (orange_2 == self.id and orange_2_isMortgaged):
				return ("M",[19])
			
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			pass
		
		def respondTrade(self,state):
			return True
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			self.erronous_bstm_counter = 0
			self.trade_status = None
			
		def getBSMTDecision(self, state):
			pink_2 = state.getPropertyOwner(14)
			orange_2 = state.getPropertyOwner(19)
			orange_2_isMortgaged = state.isPropertyMortgaged(19)
			
			if (orange_2 == self.id and not orange_2_isMortgaged):
				return ("M",[19])
			
			return None
		
		def getTradeDecision(self, state):
			pink_2 = state.getPropertyOwner(14)
			orange_2 = state.getPropertyOwner(19)
			orange_2_isMortgaged = state.isPropertyMortgaged(19)
			
			if (orange_2_isMortgaged) and (pink_2 == "1") and (self.trade_status==None):
				return ("1",50,[19],0,[14])
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return False
		
		def receiveState(self, state):
			phase = state.getPhase()
			if phase == 1:#Trade Offer Phase
				(self.trade_status,otherAgentId,cashOffer,propertiesOffer,cashRequest,propertiesRequest) = state.getPhasePayload()
	
	print("\nTest Case: Trade involving one mortgaged item. The item is unmortgaged in the next turn.")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[1,5],[5,6],[1,1],[5,4],[2,6],[5,4],[6,3],[2,3],[4,3] ],None,[0])
	
	expected_output = {
		"cash": {"1": 1500-100-100+200-120-160+50-10-100, "2": 1500-140-200+100-150-200-50},
		"position": {"1": 14, "2": 35},
		"properties":[( 6,Property(0,False,True,"1") ),( 8,Property(0,False,True,"1") ),
					( 9,Property(0,False,True,"1") ),( 11,Property(0,False,True,"2") ),
					( 14,Property(0,False,True,"2") ),( 19,Property(0,False,True,"1") ),
					( 28,Property(0,False,True,"2") ),( 35,Property(0,False,True,"2") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_utility_chance_card_owned(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return 5
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return 0
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Player falls on the Chance card which makes you advance to nearest Utility. But it is owned. Checking if rent is correctly calculated.")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[6,6],[1,2],[4,3],[6,4]],[3],None)
	
	expected_output = {
		"cash": {"1": 1500-150-200+100, "2": 1500-100},
		"position": {"1": 15, "2": 12},
		"properties":[( 12,Property(0,False,True,"1") ),( 15,Property(0,False,True,"1") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

def testcase_railroad_chance_card_owned(adjudicator):
	class AgentOne:
		def __init__(self, id):
			self.id = id
		
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
	
		def buyProperty(self, state):
			return True
		
		def auctionProperty(self, state):
			return 5
		
		def receiveState(self, state):
			pass
		
	class AgentTwo:
		def __init__(self, id):
			self.id = id
			
		def getBSMTDecision(self, state):
			return None
		
		def getTradeDecision(self,state):
			return None
			
		def buyProperty(self, state):
			return True
	
		def auctionProperty(self, state):
			return 0
		
		def receiveState(self, state):
			pass
	
	print("\nTest Case: Player falls on the Chance card which makes you advance to nearest Railroad. But it is owned. Checking if rent is correctly calculated.")
	
	agentOne = AgentOne("1")
	agentTwo = AgentTwo("2")
	[winner,final_state] = adjudicator.runGame([agentOne,agentTwo],[[6,6],[1,2],[4,3]],[5],None)
	
	expected_output = {
		"cash": {"1": 1500-150-200+50, "2": 1500-50},
		"position": {"1": 15, "2": 15},
		"properties":[ ( 12,Property(0,False,True,"1") ),( 15,Property(0,False,True,"1") )]
	}
	
	result = compare_states(final_state,expected_output)
	
	if result: print("Pass")
	else:
		print("Fail")
		print("Received Output:")
		print(final_state)
	
	return result

"""
print("Testcase flow Description:")
print("Turn 0:")
print("AgentOne falls on Oriental Avenue and buys it.")
print("Turn 1:")
print("AgentTwo falls on St. Charles Avenue and buys it.")
print("Turn 2:")
print("AgentOne falls on Vermont Avenue and buys it. Double Roll.")
print("AgentOne falls on Community Chest. Advance to Go.")
print("Turn 3:")
print("AgentTwo falls on New York Avenue and buys it.")
print("Turn 4:")
print("AgentOne falls on Connecticut Avenue and buys it. Completes the Monopoly.")
print("During the post turn BSTM, AgentOne purchases 4 houses, with 2 houses on Vermont Avenue.")
print("In the second testcase,additionally, during the post turn BSTM, AgentOne sells 2 houses, one from Oriental Avenue and one from Vermont Avenue.")
print("Turn 5:")
print("AgentTwo falls on Water Works and buys it.")
print("From this point, on events are only for the trade testcase")
print("Turn 6:")
print("AgentOne falls on Virginia Avenue and buys it.")
print("During the post turn BSTM, AgentTwo proposes a trade of $50 and New York Avenue for Virginia Avenue.")
print("AgentOne accepts.\n")
"""
print("This testcase validates the following:")

"""
"""
#20 Testcases in total
tests = [
	testcase_auction,
	testcase_payment,
	testcase_buying_houses,
	testcase_selling_houses,
	testcase_trade,
	testcase_buying_houses_invalid_1,
	testcase_buying_houses_invalid_2,
	testcase_mortgaging_unmortgaging,
	testcase_invalid_mortgaging,
	testcase_auction_for_invalid_action,
	testcase_trade_for_invalid_action,
	testcase_buyproperty_for_invalid_action,
	testcase_buying_two_hotels,
	testcase_invalid_hotel,
	testGettingOutOfJail,
	testcase_three_jails_a_day_keeps_the_lawyer_away,
	testcase_three_jails_a_day_keeps_the_lawyer_away_2,
	testcase_selling_hotel_aftermax,
	testcase_trade_mortgage,
	testcase_buying_max_houses,
	testcase_utility_chance_card_owned,
	testcase_railroad_chance_card_owned	
]

#Execution
for test in tests:
	adjudicator = Adjudicator()
	test(adjudicator)