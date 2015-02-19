from model import UserInfo
from model import ItemInfo
from dbcom import Connector
from datacenter import DataCenter 

class Controller:
    """Interface to datacenter."""
    def __init__(self):
        self.com = Connector()
        self.data = DataCenter()

    def GetTopRank(self, username, typ):
        uid = self.com.CheckUid(username);
        if typ==0:
            lst = self.data.TopRank(uid)
        else:
            maskItem = self.com.GetItemMask(typ);
            lst = self.data.TopRank(uid, itemmask = maskItem)
        
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
        if typ==0:
            maskItem = None;
        else:
            maskItem = self.com.GetItemMask(typ);
        sim = self.data.GetSimilarity(uida, uidb, maskItem)
        pr = DataCenter.Normalize(sim)
        ra = self.data.GetRankOf(uida, uidb, maskItem) # From A's view, B's rank
        rb = self.data.GetRankOf(uidb, uida, maskItem) # From B's view, A's rank
        return (una, unb, pr, ra, rb)

    def GetFeedback(self, ua, ub, typ):
        if typ==0:
            maskItem = None;
        else:
            maskItem = self.com.GetItemMask(typ);
        lst = self.data.GetPosItem(ua, ub, maskItem)
        rtn = [];
        for x in lst:
            iid = self.com.CheckItemid(x)
            iname = self.com.CheckItemName(iid)
            rtn.append([iid,iname])
        return rtn;

    def GetNegFeedback(self, ua, ub, typ):
        if typ==0:
            maskItem = None;
        else:
            maskItem = self.com.GetItemMask(typ);
        lst = self.data.GetNegItem(ua, ub, maskItem)
        rtn = [];
        for x in lst:
            iid = self.com.CheckItemid(x)
            iname = self.com.CheckItemName(iid)
            rtn.append([iid,iname])
        return rtn;