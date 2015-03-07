import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from flask.ext.cache import Cache
from config import *

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqldb://%s:%s@%s/%s?charset=utf8&use_unicode=0'%(MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST,MYSQL_DBNAME)
app.secret_key=os.urandom(24)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_RESOURCES'] = {r"/similarity/*": {"origins": r"http://api.bgm.tv/*"}}

cache = Cache(app,config={'CACHE_TYPE': 'memcached', 'CACHE_MEMCACHED_SERVERS': ['127.0.0.1:11211']})

cors = CORS(app)

db = SQLAlchemy(app)
db.create_all()

from app import views,model