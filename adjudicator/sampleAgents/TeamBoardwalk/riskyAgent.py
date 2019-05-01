import sys
from os import environ
from board import Type, Group
from state import State
from baseAgent import BaseAgent

class RiskyAgent(BaseAgent):
	def startGame(self,state):
		self.pid = self.id
		self.minMoney = 200
		self.stealing = False
	
	def startTurn(self,state):
		return None
	
	def endTurn(self,state):
		return None
	
	def getBSMDecision(self, state):
		state = State(state)
		if state.money[self.pid] - state.debt[self.pid].getTotalDebt() < 0:
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

	def respondTrade(self, state):
		return False

	def buyProperty(self, state):
		state = State(state)
		prop = state.properties[state.phaseData]
		print("Inside buyListener for "+str(self.pid)+" with prop id: "+str(prop))
		opponents = state.getOpponents(self.pid)
		bestGroup = self.getBestGroupToImprove(state)
		if bestGroup: return False
		self.stealing = True
		for opponent in opponents:
			if state.money[opponent] >= prop.data.price:
				self.stealing = False
		if self.stealing: return False
		return True

	def auctionProperty(self, state):
		state = State(state)
		print("Inside auctionListener for "+str(self.pid)+" with prop id: "+str(state.phaseData))
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

	def jailDecision(self, state):
		state = State(state)
		if self.getSafeMoney(state) > self.minMoney:
			return "R"
		else:
			return "P"

	def receiveState(self, state):
		pass

	def getTradeDecision(self,state):
		return None
	  
	def endGame(self,winner):
		if isinstance(winner, dict):
			print("Total Stats:")
			print(winner)
		else:
			print("************* The winner is player {} *************".format(winner))

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
					railroadCount = 0
					for opponent in state.getOpponents(self.pid):
						railroadCount += state.getRailroadCount(opponent)
					rent = 25 * 2 ** railroadCount
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

	