import pickle
from settings import TYPE_LIST,L
from scipy.sparse.linalg import svds
import numpy as np

fr = open('dat/mat.dat','rb')
rateInfo = pickle.load(fr)
fr.close()

def train(rateInfo,Ut,Vt):
    dp=np.zeros(shape=P.shape)
    dq=np.zeros(shape=Q.shape)
    cnt=0
    while cnt<=100:
        cnt+=1
        err=0;
        for i in xrange(8451):
            ri = rateInfo['anime']['utiliary_mtx'].getrow(i)
            for j in ri.nonzero()[1]:
                dp[:,i]+=(-2)*(ri[0,j]-np.dot(P[:,i],Q[:,j]))*Q[:,j]
            dp[:,i]+=0.1*2*P[:,i]
            err+=norm(dp[:,i])
        for j in xrange(121126):
            rj = rateInfo['anime']['utiliary_mtx'].getcol(j)
            for i in rj.nonzero()[0]:
                dq[:,j]+=(-2)*(rj[i,0]-np.dot(P[:,i],Q[:,j]))*P[:,i]
            dq[:,j]+=0.1*2*Q[:,j]
            err+=norm(dp[:,i])
        Q=Q-0.1*dq
        P=P-0.1*dp
        print err

UC={}

for tp in TYPE_LIST:
    U,S,Vt=svds(rateInfo[tp]['utiliary_mtx'],k=200)
    Ut=U.T
    # Training Process.
    # As you can see, Pt is same shape as Ut, Q is the same shape as Vt
    Pt,Q=train(rateInfo,Ut,Vt)
    UtiliaryMtx = constructUM(rateInfo,Pt,Q)
    [U,S,Vt]=svd(UtiliaryMtx)
    UC[tp]=U[:,0:100]

fw = open('dat/userconcept.dat','wb')
pickle.dump(UC,fw)
fw.close()