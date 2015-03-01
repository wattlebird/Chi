import cPickle
from numpy import array
from scipy.sparse import coo_matrix
from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from random import seed, random, shuffle
import numpy as np
import h5py
from scipy.sparse.linalg import svds

fr = open('dat/db.dat','rb')
imask = cPickle.load(fr)
umask = cPickle.load(fr)
fr.close()
fr = open('dat/mat.dat','rb')
cPickle.load(fr)
tableUI = cPickle.load(fr)
tableII = cPickle.load(fr)
fr.close()

seed()

### Phase of selecting an item type

tp = 'anime'

states = ["wish","do","collect","on_hold","dropped","all","states"];

M = session.query(Record.name).filter(Record.typ==tp).group_by(Record.name).count()
N = session.query(Record.iid).filter(Record.typ==tp).group_by(Record.iid).count()

c = session.query(Record).filter(Record.typ==tp, Record.rate != None).count()
irow=dict()
icol=dict()
data=dict()
for s in states:
    irow[s]=[]
    icol[s]=[]
    data[s]=[]

for q in session.query(Record.name, Record.iid, Record.rate, Record.state).filter(Record.typ==tp, Record.rate != None).all():
    i = umask[tp][:,:tableUI[q.name]+1].sum()-1
    j = imask[tp][:,:tableII[q.iid]+1].sum()-1
    irow['all'].append(i)
    icol['all'].append(j)
    data['all'].append(float(q.rate))
    irow[q.state].append(i)
    icol[q.state].append(j)
    data[q.state].append(True)

S = coo_matrix((data['all'],(irow['all'],icol['all'])),dtype='f',shape=(M,N))
sm=dict()
for i in xrange(5):
    sm[states[i]]=coo_matrix((data[states[i]],(irow[states[i]],icol[states[i]])),dtype='b',shape=(M,N))

d = {"wish":0,"do":1,"collect":2,"on_hold":3,"dropped":4}
for q in session.query(Record.name, Record.iid, Record.state).filter(Record.typ==tp).all():
    i = umask[tp][:,:tableUI[q.name]+1].sum()-1
    j = imask[tp][:,:tableII[q.iid]+1].sum()-1
    irow['states'].append(i)
    icol['states'].append(j)
    data['states'].append(d[q.state])

States = coo_matrix((data['states'],(irow['states'],icol['states'])),dtype='i',shape=(M,N))

t = range(S.data.shape[0])
shuffle(t)
tm=dict()
irow['train']=np.array(irow['all'])[t[:int(len(t)*0.7)]]
icol['train']=np.array(icol['all'])[t[:int(len(t)*0.7)]]
irow['validate']=np.array(irow['all'])[t[int(len(t)*0.7):int(len(t)*0.9)]]
icol['validate']=np.array(icol['all'])[t[int(len(t)*0.7):int(len(t)*0.9)]]
irow['test']=np.array(irow['all'])[t[int(len(t)*0.9):]]
icol['test']=np.array(icol['all'])[t[int(len(t)*0.9):]]
tm['train']=coo_matrix(([True]*irow['train'].shape[0],(irow['train'],icol['train'])),dtype='b',shape=(M,N))
tm['validate']=coo_matrix(([True]*irow['validate'].shape[0],(irow['validate'],icol['validate'])),dtype='b',shape=(M,N))
tm['test']=coo_matrix(([True]*irow['test'].shape[0],(irow['test'],icol['test'])),dtype='b',shape=(M,N))

U=S.multiply(tm['train']).tolil()
U_sum = U.sum(axis=1)
U_cnt = U.getnnz(axis=1)

for i in xrange(M):
    for j in U[i].rows[0]:
        if U_cnt[i]:
            U[i,j]-=U_sum[i,0]/U_cnt[i]

Uvalidate = S.multiply(tm['validate']).tolil()
U2_sum = Uvalidate.sum(axis=1)
U2_cnt = Uvalidate.getnnz(axis=1)
for i in xrange(M):
    for j in Uvalidate[i].rows[0]:
        if U_cnt[i]:
            Uvalidate[i,j]-=U_sum[i,0]/U_cnt[i]
        elif U2_cnt[i]:
            Uvalidate[i,j]-=U2_sum[i,0]/U2_cnt[i]

Utest = S.multiply(tm['test']).tolil()
U2_sum = Utest.sum(axis=1)
U2_cnt = Utest.getnnz(axis=1)
for i in xrange(M):
    for j in Utest[i].rows[0]:
        if U_cnt[i]:
            Utest[i,j]-=U_sum[i,0]/U_cnt[i]
        elif U2_cnt[i]:
            Utest[i,j]-=U2_sum[i,0]/U2_cnt[i]

Bu = np.zeros((M,5))
Bi = np.zeros((N,5))

for i in xrange(5):
    U_temp = U.multiply(sm[states[i]])
    U_sum = U_temp.sum(axis=1)
    U_cnt = U_temp.getnnz(axis=1)
    for j in xrange(M):
        if U_cnt[j]:
            Bu[j,i]=U_sum[j,0]/U_cnt[j]

for i in xrange(5):
    U_temp = U.multiply(sm[states[i]])
    U_sum = U_temp.sum(axis=0)
    U_cnt = U_temp.getnnz(axis=0)
    for j in xrange(N):
        if U_cnt[j]:
            Bi[j,i]=U_sum[0,j]/U_cnt[j]

u,s,vt = svds(U,k=800)
    
#f = h5py.File("data.hdf5","w")
#f.create_dataset("Buser",(M,5),'f')
#f['Buser'][:] = Bu
#f.create_dataset("Bitem",(N,5),'f')
#f['Bitem'][:] = Bi

#u,s,vt = svds(U,k=500)
#f.create_dataset("u",(M,500),'f')
#f['u'][:]=u
#f.create_dataset("vt",(500,N),'f')
#f['vt'][:]=vt


fw = open('dat/training-'+tp+'.dat','wb')
#cPickle.dump(S,fw)
#cPickle.dump(sm,fw)
#cPickle.dump(tm,fw)
cPickle.dump(U,fw)
cPickle.dump(Uvalidate,fw)
cPickle.dump(Utest,fw)
cPickle.dump(States,fw)
cPickle.dump(Bu,fw)
cPickle.dump(Bi,fw)
cPickle.dump(u,fw)
cPickle.dump(vt,fw)
fw.close()


