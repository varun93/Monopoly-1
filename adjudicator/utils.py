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