import cPickle
from model import UserInfo
from model import ItemInfo
from util import getnickname, getitemname

fr = open('dat/db.dat','rb')
imask = cPickle.load(fr)
umask = cPickle.load(fr)
fr.close()

class Connector(object):

    def CheckUserexists(self, username):
        q = UserInfo.query.get(username)
        return not q is None

    def CheckUid(self, username):
        q = UserInfo.query.get(username)
        return q.index

    def CheckUsername(self, uid):
        q = UserInfo.query.filter(index = uid).first()
        return q.name

    def CheckNickname(self, username):
        return getnickname(username)

    def GenerateItemMask(self, typ):
        if typ is None:
            return None
        else:
            return imask[typ]

    def GenerateUserMask(self, typ, acl):
        if typ is None and acl is None:
            return None
        else:
            return umask[typ].mulitply(umask[int(acl)])
        
    def CheckItemid(self, iindex):
        q = ItemInfo.query.filter(index = iindex).first()
        return q.i_index

    def CheckItemName(self, iid):
        return getitemname(iid)

    def GetTypeCount(self, typ):
        return umask[typ].getnnz();