from adjudicator import Adjudicator

#import Team007
#import Team001
#import TeamBoardWalk
#import TeamHarambe
#import TeamInsertName
#import TeamMaverick
#import TeamMonopoly
#import TeamNoviceGamblers
#import TeamVAR
from agents.TeamBoardwalk.team_boardwalk import RiskyAgent

agentOneId = '1'
agentTwoId = '2'
agentThreeId = '3'
agentOne = RiskyAgent(agentOneId)
agentTwo = RiskyAgent(agentTwoId)
agentThree = RiskyAgent(agentThreeId)


adjudicator = Adjudicator()
[winner,final_state] = adjudicator.runGame([agentOne, agentTwo, agentThree])
print(winner)
print(final_state)

	
	
