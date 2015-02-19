from app import db
import cPickle

db.create_all()

class Connector(object):
    def __init__(self):
        self.db=db

    def CheckUid(self, username):

    def CheckUsername(self, uid):

    def CheckNickname(self, username):

    def GetItemMask(self, typ):

    def GetUserMask(self, typ):
        
    def CheckItemid(self, iindex):

    def CheckItemName(self, iid):