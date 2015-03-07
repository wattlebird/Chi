import cPickle
from model import UserInfo
from model import ItemInfo
from util import getnickname, getitemname
from app import cache

fr = open('dat/db.dat','rb')
imask = cPickle.load(fr)
umask = cPickle.load(fr)
fr.close()

class Connector(object):
    @cache.memoize(60000)
    def CheckUserexists(self, username):
        q = UserInfo.query.get(username)
        return not q is None

    @cache.memoize(60000)
    def CheckUid(self, username):
        q = UserInfo.query.get(username)
        return q.index

    @cache.memoize(60000)
    def CheckUsername(self, uid):
        q = UserInfo.query.filter(UserInfo.index == uid).first()
        return q.name

    @cache.memoize(60000)
    def CheckNickname(self, username):
        return getnickname(username)

    def GenerateItemMask(self, typ):
        if typ is None:
            typ='all'
        return imask[typ]

    def GenerateUserMask(self, typ, acl=None):
        if typ is None:
            typ='all'
        if acl is None:
            acl=0
        return umask[typ].multiply(umask[int(acl)])
        
    @cache.memoize(60000)
    def CheckItemid(self, iindex):
        q = ItemInfo.query.filter(ItemInfo.index == iindex).first()
        return q.i_index

    @cache.memoize(60000)
    def CheckItemName(self, iid):
        return getitemname(iid)

    def GetTypeCount(self, typ):
        if typ is None:
            return umask["all"].getnnz()
        return umask[typ].getnnz()
