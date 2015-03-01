import cPickle
import numpy as np
import h5py
from numpy.linalg import norm

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
St = cPickle.load(fr)
cPickle.load(fr)
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
    return rtn

def derivative(S):
    """
    S: M x N lil sparse matrix
    U: M x 500 users vectors
    Vt 500 x N items vectors 
    Bu: M x 5 users states bias
    Bi: N x 5 items states bias
    """
    dU = np.zeros((S.shape[0],800))
    dVt = np.zeros((800, S.shape[1]))
    dBu = np.zeros((S.shape[0],5))
    dBi = np.zeros((S.shape[1],5))
    I,J = S.nonzero()
    L = S.getnnz()

    for i in xrange(L):
        s = States[I[i],J[i]]
        dU[I[i],:]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*Vt[:,J[i]].T
        dVt[:,J[i]]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*U[I[i],:].T
        dBu[I[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
        dBi[J[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
    dBu+=0.1*Bu
    dBi+=0.1*Bi
    dU+=0.1*U
    dVt+=0.1*Vt
    return (dU ,dVt, dBu, dBi)

if __name__=='__main__':
    rtn =[]
    crtn = []
    for i in xrange(100):
        rtn.append(evaluate(S))
        crtn.append(evaluate(St))
        print rtn[i]
        print crtn[i]
        dU ,dVt, dBu, dBi = derivative(S)
        U-=0.0002*dU
        Vt-=0.0002*dVt
        Bu-=0.0002*dBu
        Bi-=0.0002*dBi

    fw = open('dat/temp-'+tp+'.dat','wb')
    cPickle.dump(U,fw)
    cPickle.dump(Vt,fw)
    cPickle.dump(Bu,fw)
    cPickle.dump(Bi,fw)
    fw.close()