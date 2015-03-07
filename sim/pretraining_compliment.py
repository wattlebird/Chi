from fetch import session, Record
from scipy.sparse import coo_matrix
import cPickle

fr = open('dat/mat.dat','rb')
cPickle.load(fr)
tableUI = cPickle.load(fr)
tableII = cPickle.load(fr)
fr.close()

M = session.query(Record.name).group_by(Record.name).count()
N = session.query(Record.iid).group_by(Record.iid).count()

irow=[]
icol=[]
data=[]

d = {"wish":0,"do":1,"collect":2,"on_hold":3,"dropped":4}

for q in session.query(Record.name, Record.iid, Record.state).all():
    irow.append(tableUI[q.name])
    icol.append(tableII[q.iid])
    data.append(d[q.state])

S = coo_matrix((data,(irow,icol)),dtype='i',shape=(M,N))

fw = open('dat/training.dat','ab')
cPickle.dump(S.tolil(),fw)
fw.close()

