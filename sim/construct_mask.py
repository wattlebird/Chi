from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from sqlalchemy.sql.expression import func
from scipy.sparse import csr_matrix
import cPickle

fr = open('dat/mat.dat','rb')
cPickle.load(fr)
tableUI = cPickle.load(fr)
tableII = cPickle.load(fr)
fr.close()

imask=dict()
umask=dict()

# all item mask
count = session.query(Record.iid).group_by(Record.iid).count()
data = [True]*count
rowidx = [0]*count
colidx = range(count)
imask['all']=csr_matrix((data,(rowidx,colidx)),dtype='b',shape=(1,count))

# other item mask
for itp in ['anime','book','music','game','real']:
    scount = session.query(Record.iid).filter(Record.typ==itp).group_by(Record.iid).count()
    data = [True]*scount
    rowidx = [0]*scount
    colidx = [0]*scount
    i=0
    for q in session.query(Record.iid).filter(Record.typ==itp).group_by(Record.iid).all():
        colidx[i]=tableII[q.iid]
        i+=1
    imask[itp]=csr_matrix((data,(rowidx,colidx)),dtype='b',shape=(1,count))

# all uses mask
count = session.query(Record.name).group_by(Record.name).count()
data = [True]*count
rowidx = [0]*count
colidx = range(count)
umask['all']=csr_matrix((data,(rowidx,colidx)),dtype='b',shape=(1,count))
umask[0] = umask['all']

# users mask, of different types
for itp in ['anime','book','music','game','real']:
    scount = session.query(Record.name).filter(Record.typ==itp).group_by(Record.name).count()
    data = [True]*scount
    rowidx = [0]*scount
    colidx = [0]*scount
    i=0
    for q in session.query(Record.name).filter(Record.typ==itp).group_by(Record.name).all():
        colidx[i]=tableUI[q.name]
        i+=1
    umask[itp]=csr_matrix((data,(rowidx,colidx)),dtype='b',shape=(1,count))

# usermask, by active level
j=1
for m in ['2014-12-15','2014-07-15','2014-01-15']:
    scount = session.query(Record.name).filter(Record.adddate>=m).group_by(Record.name).count()
    data = [True]*scount
    rowidx = [0]*scount
    colidx = [0]*scount
    i=0
    for q in session.query(Record.name).filter(Record.adddate>=m).group_by(Record.name).all():
        colidx[i]=tableUI[q.name]
        i+=1
    umask[j]=csr_matrix((data,(rowidx,colidx)),dtype='b',shape=(1,count))
    j+=1

fw = open('dat/db.dat','wb')
cPickle.dump(imask,fw)
cPickle.dump(umask,fw)
fw.close()