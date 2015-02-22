import cPickle
from numpy import array
from scipy.sparse import coo_matrix
from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from random import seed, random, shuffle
import numpy as np

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

states = ["wish","do","collect","on_hold","dropped","all"];

M = session.query(Record.name).group_by(Record.name).count()
N = session.query(Record.iid).group_by(Record.iid).count()

c = session.query(Record).filter(Record.rate != None).count()
irow=dict()
icol=dict()
data=dict()
for s in states:
    irow[s]=[]
    icol[s]=[]
    data[s]=[]

for q in session.query(Record.name, Record.iid, Record.rate, Record.state).filter(Record.rate != None).all():
    irow['all'].append(tableUI[q.name])
    icol['all'].append(tableII[q.iid])
    data['all'].append(float(q.rate))
    irow[q.state].append(tableUI[q.name])
    icol[q.state].append(tableII[q.iid])
    data[q.state].append(True)

S = coo_matrix((data['all'],(irow['all'],icol['all'])),dtype='f',shape=(M,N))
sm=dict()
for i in xrange(5):
    sm[states[i]]=coo_matrix((data[states[i]],(irow[states[i]],icol[states[i]])),dtype='b',shape=(M,N))

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
Bu = np.zeros((M,5))
Bi = np.zeros((N,5))
U_sum = U.sum(axis=1)
U_cnt = U.getnnz(axis=1)

for i in xrange(M):
    for j in U[i].rows[0]:
        if U_cnt[i]:
            U[i,j]-=U_sum[i,0]/U_cnt[i]

for i in xrange(5):
    U_temp = U.multiply(sm[states[i]])
    U_sum = U.sum(axis=1)
    U_cnt = U.getnnz(axis=1)
    for j in xrange(M):
        if U_cnt[j]:
            Bu[j,i]=U_sum[j,0]/U_cnt[j]

for i in xrange(5):
    U_temp = U.multiply(sm[states[i]])
    U_sum = U.sum(axis=0)
    U_cnt = U.getnnz(axis=0)
    for j in xrange(N):
        if U_cnt[j]:
            Bi[j,i]=U_sum[0,j]/U_cnt[j]

    



fw = open('dat/training.dat','wb')
cPickle.dump(S,fw)
cPickle.dump(sm,fw)
cPickle.dump(tm,fw)
fw.close()


