import sys
import six
from os import environ
from autobahn.twisted.wamp import ApplicationRunner


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print("Game Id is mandatory!")
	else:
		from team_boardwalk import *
		# pass
		url = environ.get("CBURL", u"ws://127.0.0.1:8080/ws")
		if six.PY2 and type(url) == six.binary_type:
			url = url.decode('utf8')
		realm = environ.get('CBREALM', u'realm1')
		runner = ApplicationRunner(url, realm)
		runner.run(Component)

