import threading
from functools import wraps

def delay(delay=0.):
	"""
	Decorator emulating setTimeout method in JavaScript
	"""
	def wrap(f):
		@wraps(f)
		def delayed(*args, **kwargs):
			timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
			timer.start()
		return delayed
	return wrap

class Timer:
	toClearTimer = False
	def setTimeout(self, fn, time):
		@delay(time)
		def some_fn():
			if (self.toClearTimer is False):
				fn()
			else:
				print('Invocation is cleared!')		
		some_fn()
	def setClearTimer(self):
		self.toClearTimer = True
		
class TimeoutBehaviour:
	"""
	Used during the start of a game. The adjudicator will wait for 5 min for all the players to join.
	If all the players haven't joined by this time, based on the enum value here, the game maybe
	started anyway or stopped immediately.
	"""
	PLAY_ANYWAY = 0,
	STOP_GAME = 1

def typecast(val,thetype,default):
	"""
	Validation function which checks if the variable `var` can be typecast to datatype `thetype`.
	If there was any exception encountered, return the default value specified
	"""
	try:
		if (thetype == bool) and not isinstance(val, thetype):
			return default
		return thetype(val)
	except:
		return default
	
def check_valid_cash(cash):
	"""
	Function checks cash passed in through actions by the agent.
	If cash can't be typecast to int, the cash amount is considered 
	invalid and invalid flows for defaulting would take place.
	"""
	try:
		cash = int(cash)
	except:
		return 0
	if cash < 0:
		return 0
	return cash