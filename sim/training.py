import cPickle
import numpy as np
import h5py
from numpy.linalg import norm
from numpy import sqrt
import multiprocessing
import time

tp='anime'

#fr = open('dat/db.dat','rb')
#imask = cPickle.load(fr)
#umask = cPickle.load(fr)
#fr.close()
#fr = open('dat/training.dat','rb')
#cPickle.load(fr)
#sm = cPickle.load(fr)
#tm = cPickle.load(fr)
#fr.close()
fr = open('dat/training-'+tp+'.dat','rb')
S = cPickle.load(fr)
#St = cPickle.load(fr)
#Sv = cPickle.load(fr)
States = cPickle.load(fr)
Bu = cPickle.load(fr)
Bi = cPickle.load(fr)
U = cPickle.load(fr)
Vt = cPickle.load(fr)
fr.close()
States=States.tolil()
#f = h5py.File("data.hdf5","r")
#U = f['u']
#Vt = f['vt']
#Bu = f['Buser']
#Bi = f['Bitem']

def evaluate(S):
    """
    S: M x N lil sparse matrix
    U: M x 500 users vectors
    Vt 500 x N items vectors 
    Bu: M x 5 users states bias
    Bi: N x 5 items states bias
    """

    I,J = S.nonzero()
    L = S.getnnz()
    rtn = 0
    for i in xrange(L):
        s = States[I[i],J[i]]
        rtn+=(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])**2
    return sqrt(rtn/L)

def derivative1(S):
    dU = np.zeros((S.shape[0],800))
    dVt = np.zeros((800, S.shape[1]))
    I,J = S.nonzero()
    L = S.getnnz()
    for i in xrange(L):
        s = States[I[i],J[i]]
        dU[I[i],:]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*Vt[:,J[i]].T
        dVt[:,J[i]]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*U[I[i],:].T
    dU+=U
    dVt+=Vt
    return (dU ,dVt)

def derivative2(S):
    dBu = np.zeros((S.shape[0],5))
    dBi = np.zeros((S.shape[1],5))
    I,J = S.nonzero()
    L = S.getnnz()
    for i in xrange(L):
        s = States[I[i],J[i]]
        dBu[I[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
        dBi[J[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
    dBu+=Bu
    dBi+=Bi
    return (dBu, dBi)
    
    
def worker1(d,S):
    dU ,dVt = derivative1(S)
    d['dU']=dU
    d['dVt']=dVt
    
def worker2(d,S):
    print evaluate(S)
    dBu, dBi = derivative2(S)
    d['dBu'] = dBu
    d['dBi'] = dBi
    

if __name__=='__main__':
    try:
        for i in xrange(70):
            mgr = multiprocessing.Manager()
            d = mgr.dict()
            p1 = multiprocessing.Process(target=worker1, args=(d,S))
            p2 = multiprocessing.Process(target=worker2, args=(d,S))

            p1.start()
            p2.start()
            p1.join()
            p2.join()
            U-=0.0002*d['dU']
            Vt-=0.0002*d['dVt']
            Bu-=0.0002*d['dBu']
            Bi-=0.0002*d['dBi']
    finally:
        fw = open('dat/temp-'+tp+'.dat','wb')
        cPickle.dump(U,fw)
        cPickle.dump(Vt,fw)
        cPickle.dump(Bu,fw)
        cPickle.dump(Bi,fw)
        fw.close()