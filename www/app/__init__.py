import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import *

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqldb://%s:%s@%s/%s?charset=utf8&use_unicode=0'%(MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST,MYSQL_DBNAME)

db = SQLAlchemy(app)

from app import views,model