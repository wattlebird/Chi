from fetch import session, Record
from scipy.sparse import coo_matrix
import cPickle

fr = open('dat/mat.dat','rb')
cPickle.load(fr)
tableUI = cPickle.load(fr)
tableII = cPickle.load(fr)
fr.close()

fr = open('dat/db.dat','rb')
imask = cPickle.load(fr)
umask = cPickle.load(fr)
fr.close()

fr = open('dat/assembly.dat','rb')
bucket = cPickle.load(fr)
fr.close()

M = session.query(Record.name).group_by(Record.name).count()
N = session.query(Record.iid).group_by(Record.iid).count()

irow=[]
icol=[]
data=[]

for q in session.query(Record.name, Record.iid, Record.typ).all():
    tp = q.typ
    i = umask[tp][:,:tableUI[q.name]+1].sum()-1
    j = imask[tp][:,:tableII[q.iid]+1].sum()-1

    irow.append(tableUI[q.name])
    icol.append(tableII[q.iid])
    data.append(bucket[tp][i,j])

U = coo_matrix((data,(irow,icol)),shape=(M,N))
U = U.tocsr()
U2 = U.multiply(U)

fw = open('dat/a.dat','wb')
cPickle.dump(U,fw)
cPickle.dump(U2,fw)
fw.close()