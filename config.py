# config file 

import os
from dotenv import load_dotenv
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLE = True	
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
	SECRET_KEY = os.getenv("SECRET_KEY")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	ACCOUNT_SID = os.getenv("ACCOUNT_SID")
	ACCOUNT_TOKEN = os.getenv("ACCOUNT_TOKEN")
	SESSION_TYPE = "redis"
	REDIS_URL = os.getenv("REDIS_URL")


class production(Config):
	DEBUG = False


class staging(Config):
	DEBUG = True
	TESTING = True

class devlopment(Config):
	DEBUG = True
	TESTING = True
	ENV = "TESTING"
	SESSION_TYPE = "sqlalchemy"
	SQLALCHEMY_DATABASE_URI =  "sqlite:///" + os.path.join(basedir, 'us.db')