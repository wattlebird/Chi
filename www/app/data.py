from app import db
from model import UserInfo
import pickle
from exception import Exception
import numpy as np

fr = open('dat/w.dat','rb')
w = pickle.load(fr) # a user_num x 100 mat
fr.close()

class QueryError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Query Error: failed to get wanted item "+repr(self.value)

class DUser:
    def __init__(self, id, sim):
        self.id=id
        self.sim=sim
    

def qualified(db, username):
    q=UserInfo.query.filter_by(name=username).first()
    # q=db.session.query(UserInfo.name, UserInfo.count).filter(UserInfo.name=username).first()
    return q.count>0

def similarlist(db, username):
    q=UserInfo.query.filter_by(name=username).first()
    if q is None:
        raise QueryError(username)
    u=w[q.index,:]
    qlist=[]
