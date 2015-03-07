import cPickle
from heapq import nlargest,nsmallest
from numpy import sqrt, array, nonzero
from app import cache

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
        return round((sim+1.)/2,4)*100

    @cache.memoize(600)
    def TopRank(self, uid, itemmask, usermask):

        M=U[:,itemmask.indices]

        v = M[uid]
        vnorm = sqrt(U2[:,itemmask.indices][uid].sum(axis=1)[0,0])+1
        M=M[usermask.indices]

        unorm = self._getnorm(itemmask, usermask)
        # Now standardize information to lst, include normalize and packaging.
        simv = array(M.dot(v.T)/unorm/vnorm).squeeze(1)

        lst = self._generatenodelist(simv, usermask.indices)

        rt = nlargest(11,lst)
        rlist = []
        # if uid have favorated some items, it returns a list.
        # Otherwise, returns an empty list.
        if uid in usermask.indices:
            for x in rt[1:]:
                rlist.append([x.id, x.sim])
        return rlist

    def GetSimilarity(self, uida, uidb, itemmask):

        M=U[:,itemmask.indices]
        M2=U2[:,itemmask.indices]

        va = M[uida]
        vb = M[uidb]
        n = (sqrt(M2[uida].sum(axis=1)[0,0])+1)*(sqrt(M2[uidb].sum(axis=1)[0,0])+1)
        v = va.dot(vb.T)
        if v.getnnz()==1:
            return v.data[0]/n
        else:
            return 0

    @cache.memoize(600)
    def GetRankOf(self, uida, uidb, sim, itemmask, usermask):

        M=U[:,itemmask.indices]
        
        va = M[uida]
        vnorm = sqrt(U2[:,itemmask.indices][uida].sum(axis=1)[0,0])+1
        M=M[usermask.indices]

        simv = M.dot(va.T)/self._getnorm(itemmask, usermask)/vnorm
        return nonzero(simv>sim)[0].shape[1];


    def GetPosItem(self, uida, uidb, itemmask, usermask):

        va = U[uida]
        vb = U[uidb]
        va = va.multiply(itemmask)
        vb = vb.multiply(itemmask)
        x = va.multiply(vb)
        x.data=x.data*(x.data>2)
        x.eliminate_zeros()
        if x.getnnz()==0:
            return []
        lst = self._generatenodelist(x.data, x.indices)
        rt = nlargest(3,lst)
        rtlst = []
        for x in rt:
            rtlst.append(x.id)
        return rtlst
        

    def GetNegItem(self, uida, uidb, itemmask, usermask):

        va = U[uida]
        vb = U[uidb]
        va = va.multiply(itemmask)
        vb = vb.multiply(itemmask)
        x = va.multiply(vb)
        x.data=x.data*(x.data<-2)
        x.eliminate_zeros()
        if x.getnnz()==0:
            return []
        lst = self._generatenodelist(x.data, x.indices)
        rt = nsmallest(3,lst)
        rtlst = []
        for x in rt:
            rtlst.append(x.id)
        return rtlst

    def _generatenodelist(self, data, index):
        """ data is an one dim array, index is also an one dim array."""
        lst = []
        for i in xrange(index.shape[0]):
            lst.append(Node(id = index[i], sim = data[i]))
        return lst

    @cache.memoize(60000)
    def _getnorm(self, itemmask, usermask):
        """ return a matrix sum(usermask) x 1 """
        M=U2[:,itemmask.indices]

        M=M[usermask.indices]

        return sqrt(M.sum(axis=1))+1

