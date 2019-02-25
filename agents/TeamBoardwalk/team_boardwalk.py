import sys
from board import Type, Group
from state import State
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession
from twisted.python.failure import Failure
from autobahn import wamp



class Component(ApplicationSession):
	"""
	An application component calling the different backend procedures.
	"""

	@inlineCallbacks
	def onJoin(self, details):
		
		# print("session attached")
		
		self.id = sys.argv[1]
		self.pid = sys.argv[1]
		self.minMoney = 200
		print(self.minMoney)
		# self.test = self.pid == 0
		self.stealing = False
		
		results = []

		res = yield self.register(self)
		results.extend(res)

		for res in results:
			if isinstance(res, Failure):
				print("Failed to register procedure: {}".format(res.value))
			else:
				print("registration ID {}: {}".format(res.id, res.procedure))
	

	def onDisconnect(self):
		print("disconnected")
		reactor.stop()


	@wamp.register('monopoly.agent{}.bsm'.format(sys.argv[1]))
	def getBSMTDecision(self, state):
		state = State(state)
		if state.money[self.pid] - state.debt[self.pid].getTotalDebt() < 0:
			pos = state.positions[self.pid]
			prop = state.properties[pos]
			if pos == -1 or not (prop.data.price == state.debt[self.pid * 2 + 1] and prop.owner == -1):
				return self.getBestActionForMoney(state)
		if state.money[self.pid] < self.getSafeMoney(state):
			return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup:
			groupProps = state.getGroupProperties(bestGroup)
			cost = len(groupProps) * groupProps[0].data.houseCost
			if state.money[self.pid] < self.getSafeMoney(state) + cost:
				return self.getBestMortgageAction(state, state.getOwnedGroupProperties(self.pid))
			for prop in groupProps:
				if prop.mortgaged:
					return "M", [prop.id]
			return "B", [(prop.id, 1) for prop in groupProps]
		return None

	@wamp.register('monopoly.agent{}.respondtrade'.format(sys.argv[1]))
	def respondTrade(self, state):
		return False

	@wamp.register(u'monopoly.agent{}.buy'.format(sys.argv[1]))
	def buyProperty(self, state):
		state = State(state)
		prop = state.properties[state.phaseData]
		opponents = state.getOpponents(self.pid)
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup: return False
		self.stealing = True
		for opponent in opponents:
			if state.money[opponent] >= prop.data.price:
				self.stealing = False
		if self.stealing: return False
		return True

	@wamp.register('monopoly.agent{}.auction'.format(sys.argv[1]))
	def auctionProperty(self, state):
		state = State(state)
		data = None 
		if type(state.phaseData) is int:
			data = state.phaseData
		else:
			data = state.phaseData[0] 
		prop = state.properties[data]
		opponents = state.getOpponents(self.pid)
		bid = prop.data.price // 2 + 1
		if self.stealing:
			bid = prop.data.price
			self.stealing = False
		maxOpponent = 0
		for opponent in opponents:
			if state.money[opponent] > maxOpponent:
				maxOpponent = state.money[opponent]
		if maxOpponent < bid: bid = maxOpponent
		return min(state.money[self.pid], bid)

	@wamp.register('monopoly.agent{}.jail'.format(sys.argv[1]))
	def jailDecision(self, state):
		state = State(state)
		if self.getSafeMoney(state) > self.minMoney:
			return "R"
		else:
			return "P"

	@wamp.register('monopoly.agent{}.receivestate'.format(sys.argv[1]))
	def receiveState(self, state):
		pass

	@wamp.register('monopoly.agent{}.trade'.format(sys.argv[1]))
	def getTradeDecision(self,state):
		return None

	def getExpectedRent(self, prop, houses, turn):
		data = prop.data
		opponentTurnsLeft = (100 - turn) / 2
		return data.rents[houses] * data.probability * opponentTurnsLeft

	def getSafeMoney(self, state):
		maxRent = 0
		for prop in state.properties:
			if (prop.owned and prop.owner == self.pid) or prop.id >= 40: continue
			rent = 0
			if prop.data.type == Type.PROPERTY:
				rent = prop.data.rents[prop.houses]
			if prop.data.type == Type.RAILROAD:
				rent = 25 * 2 ** 2
			if rent > maxRent: maxRent = rent
		return self.minMoney

	def getBestGroupToImprove(self, state):
		ownedGroups = state.getOwnedBuildableGroups(self.pid)
		maxRoi = 0
		bestGroup = None
		bestGroups = [Group.ORANGE, Group.LIGHT_BLUE, Group.RED, Group.PINK, Group.DARK_BLUE, Group.YELLOW, Group.GREEN, Group.BROWN]
		for group in bestGroups:
			if state.playerOwnsGroup(self.pid, group):
				groupProps = state.getGroupProperties(group)
				if groupProps[0].houses < 5: return group
		# for group in ownedGroups:
		#	 props = state.getGroupProperties(group)
		#	 if props[0].houses == 5: continue
		#	 rent = sum([self.getExpectedRent(prop, prop.houses, state.turn) for prop in props])
		#	 improvedRent = sum([self.getExpectedRent(prop, prop.houses + 1, state.turn) for prop in props])
		#	 cost = len(props) * props[0].data.houseCost
		#	 roi = (improvedRent - rent) / cost
		#	 if roi > maxRoi:
		#		 maxRoi = roi
		#		 bestGroup = group
		return bestGroup

	def getBestMortgageAction(self, state, ignoredProps):
		props = state.getOwnedProperties(self.pid)
		maxRatio = 0
		bestProp = None
		for prop in props:
			if not prop.mortgaged and prop not in ignoredProps and prop.houses == 0:
				rent = 1
				if prop.data.type == Type.PROPERTY:
					rent = prop.data.rents[prop.houses]
				if prop.data.type == Type.RAILROAD:
					rent = 25 * 2 ** state.getRailroadCount((self.pid + 1) % 2)
				ratio = (prop.data.price // 2) / rent
				if ratio > maxRatio:
					maxRatio = ratio
					bestProp = prop
		if bestProp: return "M", [bestProp.id]
		return None

	def getBestActionForMoney(self, state):
		mortgageAction = self.getBestMortgageAction(state, [])
		if mortgageAction: return mortgageAction
		ownedGroups = state.getOwnedBuildableGroups(self.pid)
		for group in ownedGroups:
			groupProps = state.getGroupProperties(group)
			if groupProps[0].houses > 0:
				return "S", [(prop.id, 1) for prop in groupProps]


