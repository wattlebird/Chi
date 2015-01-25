from app import db
from model import UserInfo
import pickle
from random import seed, randint
from heapq import nlargest

seed()

fr = open('dat/a.dat','rb')
U = pickle.load(fr) # a user_num x 100 mat
unorm = pickle.load(fr)
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
    

def qualified(db, username):
    q=UserInfo.query.filter_by(name=username).first()
    # q=db.session.query(UserInfo.name, UserInfo.count).filter(UserInfo.name=username).first()
    if q and q.count:
        return 1
    elif q:
        return 0
    else:
        return -1


def similarlist(db, username):
    q=UserInfo.query.filter_by(name=username).first()
    if q is None:
        raise QueryError(username)
    simv=U.dot(U[q.index,:].T).toarray()
    qlist=[]
    for i in xrange(U.shape[0]):
        qlist.append(DUser(id=i,
        sim=simv[i][0]/(unorm[q.index]*unorm[i])))
    slist=nlargest(11,qlist)
    rlist=[]
    for i in xrange(1,11):
        q=UserInfo.query.filter_by(index=slist[i].id).first()
        rlist.append((q.name,round(_normalize(slist[i].sim),4)))
    return rlist

def getsim(db, username, candidate):
    q=UserInfo.query.filter_by(name=username).first()
    if q is None:
        raise QueryError(username)
    u=U[q.index,:]
    p=UserInfo.query.filter_by(name=candidate).first()
    if p is None:
        raise QueryError(username)
    v=U[p.index,:]
    return _normalize(u.dot(v.T).toarray()[0][0]/(unorm[q.index]*unorm[p.index]))

def _pick_top_ten(qlist):
    _qpick_ten(qlist,0,len(qlist))
    _insort(qlist,0,11)
    return qlist[1:11]

def _qpick_ten(a,b,e):
    if e>11:
        i=randint(b,e-1)
        a[b],a[i]=a[i],a[b]
        i=j=1
        while i!=e:
            if a[b]<a[i]:
                a[i],a[j]=a[j],a[i]
                j+=1
            i+=1
        a[b],a[j-1]=a[j-1],a[b]
        if j==11:
            return
        elif j>11:
            _qpick_ten(a,b,j)
        else:
            _qpick_ten(a,j,e)

def _insort(a,b,e):
    for i in xrange(b+1,e):
        key=a[i]
        j=i-1
        while j>=0:
            if a[j]>key:
                break
            a[j+1]=a[j]
            j-=1
        a[j+1]=key

def _normalize(num):
    return (num+1)/2