# config file 

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	debug = False
	testing = False
	CSRF_ENABLE = True	
	SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_URL']
	SECRET_KEY = os.environ["SECRET_KEY"]


class production(object):
	debug = False


class staging(object):
	debug = True
	testing = True

class devlopment(object):
	debug = True
	testing = True