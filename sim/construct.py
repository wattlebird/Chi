import numpy as np
from scipy import sparse
from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from sqlalchemy.sql.expression import func
from settings import TYPE_LIST
import pickle

#tableState = {'do':1,'collect':2,'wish':3,'on_hold':4,'dropped':5}
tableUI=dict()
tableII=dict()
userAvg=dict()



for usr in session.query(UserInfo.name, UserInfo.index, UserInfo.average).filter(UserInfo.index != None).all():
    tableUI[usr.name]=usr.index

for rec in session.query(ItemInfo.i_index, ItemInfo.index).all():
    tableII[rec.i_index]=rec.index

#nUsers=session.query(UserInfo).filter(UserInfo.index!=None).count()
nItms=session.query(ItemInfo).count()

gp=dict()
gp['bias_states']={}
global_avg=session.query(func.avg(Record.rate).label('average')).filter(Record.rate!=None).scalar();
for q in session.query(Record.state, func.avg(Record.rate).label('average')).\
    filter(Record.rate != None).group_by(Record.state):
    gp['bias_states'][q.state]=float(q.average)-float(global_avg)

nFaved = session.query(Record).count()
data = np.zeros(nFaved)
i = np.zeros(nFaved)
j = np.zeros(nFaved)
idx=0
for q in session.query(Record.name, Record.iid, Record.state, Record.rate):
    p = session.query(UserInfo.name, UserInfo.sd, UserInfo.ratecount, UserInfo.average).filter(UserInfo.name==q.name).first()
    
    try:
        if q.rate!=None and p.ratecount>3 and p.sd>0.1:
            data[idx]=q.rate-p.average
        else:
            data[idx]=gp['bias_states'][q.state]
    except AttributeError, e:
        print "Exception: for "+q.name+" we cannot find the user.\n"
        continue

    i[idx]=tableUI[q.name]
    j[idx]=tableII[q.iid]
    idx+=1
gp['utiliary_mtx']=sparse.coo_matrix((data,(i,j))).tolil()

fw = open('dat/mat.dat','wb')
pickle.dump(gp,fw)
pickle.dump(tableUI,fw)
pickle.dump(tableII,fw)
fw.close()