"""
Farmfresh
date: 5-1-20
ver: 1
"""

# importing modules
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
# app intance and some config
load_dotenv(override=True)

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTING'))
db = SQLAlchemy(app) 




@app.route('/')
def main():
	
	return "<h1>ok<h1>"


if __name__  == "__main__":
	app.run()