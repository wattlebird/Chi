import cPickle
from heapq import nlargest,nsmallest
from numpy import sqrt

fr = open('dat/a.dat','rb')
U = cPickle.load(fr)
U2 = cPickle.load(fr)
fr.close()

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
    def Normalize(sim):
        return round((sim+1)/2,4)*100

    def TopRank(self, uid, itemmask, usermask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]

        v = M[uid]
        if usermask:
            # Here, usermask should also be a row vector.
            M=M[usermask.indices]

        # Now standardize information to lst, include normalize and packaging.
        simv = array(M.dot(v.T)/_getnorm(itemmask, usermask)).squeeze(1)
        if usermask:
            lst = _generatenodelist(simv, usermask.indices)
        else:
            lst = _generatenodelist(simv, range(M.shape[0]))

        rt = nlargest(11,lst)
        rlist = []
        # if uid have favorated some items, it returns a list.
        # Otherwise, returns an empty list.
        if uid in usermask.indices:
            for x in rt:
                rlist.append([x.id, x.sim])
        return rlist

    def GetSimilarity(self, uida, uidb, itemmask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]

        va = M[uida]
        vb = M[uidb]
        n = (sqrt(U2[uida])+1)(sqrt(U2[uidb])+1)
        return va.dot(vb.T)/n


    def GetRankOf(self, uida, uidb, sim, itemmask, usermask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]
        
        va = M[uida]
        if usermask:
            # Here, usermask should also be a row vector.
            M=M[usermask.indices]

        simv = M.dot(va.T)
        return (simv>sim).getnnz();


    def GetPosItem(self, uida, uidb, itemmask, usermask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]

        va = M[uida]
        vb = M[uidb]
        x = va.multiply(vb)
        x = x.multiply(x>0)
        lst = _generatenodelist(x.data, x.indices)
        rt = nlargest(3,lst)
        rtlst = []
        for x in rt:
            rtlst.append(x.id)
        return rtlst
        

    def GetNegItem(self, uida, uidb, itemmask, usermask):
        if not itemmask:
            M=U
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U[:,itemmask.indices]

        va = M[uida]
        vb = M[uidb]
        x = va.multiply(vb)
        x = x.multiply(x<0)
        lst = _generatenodelist(x.data, x.indices)
        rt = nsmallest(3,lst)
        rtlst = []
        for x in rt:
            rtlst.append(x.id)
        return rtlst

    def _generatenodelist(self, data, index):
        """ data is an one dim array, index is also an one dim array."""
        lst = []
        for i in index.shape[0]:
            lst.append(id = index[i], sim = data[i])
        return lst

    def _getnorm(self, itemmask, usermask):
        """ return a matrix sum(usermask) x 1 """
        if not itemmask:
            M=U2
        else:
            # Notice! Here itemmask should be a 1 x N row csr sparse matrix. 
            # So itemmask.indices should return all indexs that are not zero.
            M=U2[:,itemmask.indices]

        if usermask:
            # Here, usermask should also be a row vector.
            M=M[usermask.indices]

        return sqrt(M.sum(axis=1))+1

