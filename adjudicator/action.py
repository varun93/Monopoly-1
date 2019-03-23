import six
import abc
from dice import Dice

@six.add_metaclass(abc.ABCMeta)
class Action:
	
	#context should include: all the singleton action instances
	#(or the instances required by a given action), gameId, agentId
	def __init__(self,context):
		self.context =  context
	
	@abc.abstractmethod
	def publish(self):
		"""
		Publishes an action on the agent's channel.
		"""	
	
	@abc.abstractmethod
	def subscribe(self,*args,**kwargs):
		"""
		Callback invoked by the agent when it is done with an action.
		"""