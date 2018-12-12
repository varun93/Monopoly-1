from adjudicator import Adjudicator

import Team007
import Team001
import TeamBoardWalk
import TeamHarambe
import TeamInsertName
import TeamMaverick
import TeamMonopoly
import TeamNoviceGamblers
import TeamVAR

agents = {
1:Team001, #
2:TeamMonopoly, #Working
3:TeamBoardWalk, #Working
4:TeamHarambe, #Working
5:TeamInsertName, #Working
6:TeamMaverick, #Working
7:Team007, #Working
8:TeamNoviceGamblers, #Working
9:TeamVAR #Working
}

#orderings = [(7,4)]
#orderings = [(1,8),(2,7),(3,6),(4,5),(8,9),(7,1),(6,2),(5,3),(2,9),(3,8),(4,7),(5,6),(9,1),(8,2),(7,3),(6,4),(3,1),(4,9),(5,8),(6,7),(1,2),(9,3),(8,4),(7,5),(4,2),(5,1),(6,9),(7,8),(2,3),(1,4),(9,5),(8,6),(9,7),(1,6),(2,5),(3,4)]
orderings = [(8,4),(4,2),(1,4),(3,4)]
#orderings = [(4,9)]


NO_OF_GAMES = 100

for ordering in orderings:
	winners = []
	final_states = []
	
	#if 4 in ordering:
		#Skipping team harambe
	#	continue
	
	for i in range(1, NO_OF_GAMES+1):
		
		if i>(NO_OF_GAMES/2):
			agentOneId = ordering[0]
			agentTwoId = ordering[1]
			agentOne = agents[agentOneId].Agent(1)
			agentTwo = agents[agentTwoId].Agent(2)
		else:
			agentOneId = ordering[1]
			agentTwoId = ordering[0]
			agentOne = agents[agentOneId].Agent(1)
			agentTwo = agents[agentTwoId].Agent(2)
		
		adjudicator = Adjudicator()
		[winner,final_state] = adjudicator.runGame(agentOne, agentTwo)
		if winner == 1:
			winners.append(agentOneId)
		elif winner == 2:
			winners.append(agentTwoId)
		elif winner == 0:
			winners.append(0)
		
		if i%5==0:
			print("Game "+str(i)+" completed")
		
		final_states.append(final_state)
		for winner in winners:
			f.write(str(winner)+"\n")
		g.write("turn|properties|position|cash\n")
		for final_state in final_states:
			g.write(str(final_state[0])+"|"+str(final_state[1])+"|"+str(final_state[2])+"|"+str(final_state[3])+"\n")

	f = open("winners_"+str(agentOneId)+str(agentTwoId)+".txt", "w")
	g = open("final_states_"+str(agentOneId)+str(agentTwoId)+".txt", "w")
	f.write("winners\n")
	
	print("Results:")
	print("Agent "+str(agents[agentOneId])+" wins: "+str(winners.count(agentOneId))+" games")
	print("Agent "+str(agents[agentTwoId])+" wins: "+str(winners.count(agentTwoId))+" games")
	print("Ties: "+str(winners.count(0))+" games")
		
	input("Press Enter to continue...")

	
	
