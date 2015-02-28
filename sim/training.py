import cPickle
import numpy as np
import h5py
from numpy.linalg import norm


#fr = open('dat/db.dat','rb')
#imask = cPickle.load(fr)
#umask = cPickle.load(fr)
#fr.close()
#fr = open('dat/training.dat','rb')
#cPickle.load(fr)
#sm = cPickle.load(fr)
#tm = cPickle.load(fr)
fr.close()
fr = open('dat/training.dat','rb')
S = cPickle.load(fr)
St = cPickle.load(fr)
cPickle.load(fr)
States = cPickle.load(fr)
fr.close()

f = h5py.File("data.hdf5","r")
U = f['u']
Vt = f['vt']
Bu = f['Buser']
Bi = f['Bitem']

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
        s = States[i,j]
        rtn+=(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])**2
    rtn+=(norm(U, axis=1).sum()+norm(Vt, axis=0).sum()+norm(Bu, axis=1)+norm(Bi,axis=1))/2
    return rtn

def derivative(S):
    """
    S: M x N lil sparse matrix
    U: M x 500 users vectors
    Vt 500 x N items vectors 
    Bu: M x 5 users states bias
    Bi: N x 5 items states bias
    """
    dU = np.zeros((S.shape[0],500),dtype=np.float32)
    dVt = np.zeros((500, S.shape[1]),dtype=np.float32)
    dBu = np.zeros((S.shape[0],5),dtype=np.float32)
    dBi = np.zeros((S.shape[1],5),dtype=np.float32)
    I,J = S.nonzero()
    L = S.getnnz()

    for i in xrange(L):
        s = States[i,j]
        dU[I[i],:]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*Vt[:,J[i]].T
        dVt[:,J[i]]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])*U[I[i],:].T
        dBu[I[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
        dBi[J[i],s]+=-2*(S[I[i],J[i]]-U[I[i],:].dot(Vt[:,J[i]])-Bu[I[i],s]-Bi[J[i],s])
    dBu+=Bu
    dBi+=Bi
    dU+=U
    dVt+=Vt
    return (dU ,dVt, dBu, dBi)

if __name__=='__main__':
    print evaluate(S)
    print evaluate(St)
    du, dvt, dbu, dbi = derivative(S)
    U-=0.01*dU
    Vt-=0.01*dVt
    Bu-=0.01*dBu
    Bi-=0.01*dBi
    print evaluate(S)
    print evaluate(St)