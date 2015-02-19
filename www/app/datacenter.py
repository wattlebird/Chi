import cPickle

class Node:
    def __init__(self, id, sim):
        self.id=id
        self.sim=sim

    def __lt__(self, other):
        return self.sim<other.sim

    def __le__(self, other):
        return self.sim<=other.sim

    def __eq__(self, other):
        return self.sim==other.sim

    def __ne__(self, other):
        return self.sim<>other.sim

    def __gt__(self, other):
        return self.sim>other.sim

    def __ge__(self, other):
        return self.sim>=other.sim

class DataCenter:
    def __init__(self):
        pass

    @staticmethod
    def Normalize(self, sim):
        return round((sim+1)/2,4)*100

    def TopRank(self, uid, itemmask, usermask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]

        if usermask:
            M=M[usermask.indices]

        

    def GetSimilarity(self, uida, uidb, itemmask, usermask):
        pass

    def GetRankOf(self, uida, uidb, itemmask, usermask):
        pass

    def GetPosItem(self, uida, uidb, itemmask, usermask):
        pass

    def GetNegItem(self, uida, uidb, itemmask, usermask):
        pass

    def _generatenodelist(self, )