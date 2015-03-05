from dbcom import Connector
from datacenter import DataCenter 

class Controller:
    """Interface to datacenter."""
    def __init__(self):
        self.com = Connector()
        self.data = DataCenter()

    def UserExist(self, username):
        """True if user registered before 15/01/2015"""
        return self.com.CheckUserexists(username)

    def UserRecords(self, username):
        """True if user faved at least one item."""
        return not self.com.CheckUid(username) is None

    def GetTopRank(self, username, typ, acl):
        uid = self.com.CheckUid(username);
        maskItem = self.com.GenerateItemMask(typ);
        maskUser = self.com.GenerateUserMask(typ, acl);
        lst = self.data.TopRank(uid, maskItem, maskUser)
        
        rtn = [];
        for x in lst:
            un = self.com.CheckUsername(x[0])
            unn = self.com.CheckNickname(un)
            pc = DataCenter.Normalize(x[1])
            rtn.append([un, unn, pc])
        return rtn

    def GetCouple(self, ua, ub, typ):
        """
        return(NicknameA, NicknameB, Similarity_in_percent, rankA, rankB)
        """
        una = self.com.CheckNickname(ua);
        unb = self.com.CheckNickname(ub);
        uida = self.com.CheckUid(ua);
        uidb = self.com.CheckUid(ub);
        maskItem = self.com.GenerateItemMask(typ);
        maskUser = self.com.GenerateUserMask(typ);
        sim = self.data.GetSimilarity(uida, uidb, maskItem)
        pr = DataCenter.Normalize(sim)
        ra = self.data.GetRankOf(uida, uidb, sim, maskItem, maskUser) # From A's view, B's rank
        rb = self.data.GetRankOf(uidb, uida, sim, maskItem, maskUser) # From B's view, A's rank
        return (una, unb, pr, ra, rb)

    def GetFeedback(self, ua, ub, typ):
        maskItem = self.com.GenerateItemMask(typ);
        maskUser = self.com.GenerateUserMask(typ);
        lst = self.data.GetPosItem(ua, ub, maskItem, maskUser)
        rtn = [];
        for x in lst:
            iid = self.com.CheckItemid(x)
            iname = self.com.CheckItemName(iid)
            rtn.append([iid,iname])
        return rtn;

    def GetNegFeedback(self, ua, ub, typ):
        maskItem = self.com.GenerateItemMask(typ);
        maskUser = self.com.GenerateUserMask(typ);
        lst = self.data.GetNegItem(ua, ub, maskItem, maskUser)
        rtn = [];
        for x in lst:
            iid = self.com.CheckItemid(x)
            iname = self.com.CheckItemName(iid)
            rtn.append([iid,iname])
        return rtn;

    def GetCount(self, typ):
        return self.com.GetTypeCount(typ)

    def GetUsernickname(self, username):
        return self.com.CheckNickname(username)
