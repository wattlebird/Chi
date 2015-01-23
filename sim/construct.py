import numpy as np
from scipy import sparse
from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from sqlalchemy.sql.expression import func
from settings import TYPE_LIST
import pickle

#tableState = {'do':1,'collect':2,'wish':3,'on_hold':4,'dropped':5}
tableUI=dict()
tableII=dict()

#cnt=0;
#for usr in session.query(Users.name).order_by(Users.uid).all():
#    count = session.query(Record).filter(Record.name==usr.name).count()
#    if count>0:
#        tableUI[usr.name]=cnt
#        itm = UserInfo(name=usr.name, index=cnt, count=count)
#        session.add(itm)
#        cnt+=1
#    else:
#        itm = UserInfo(name=usr.name, count=count)
#        session.add(itm)
#session.commit()
#nUsers=cnt+1

#cnt=0;
#for rec in session.query(Record.iid).group_by(Record.iid).order_by(Record.iid).all():
#    tableII[rec.iid]=cnt
#    itm = ItemInfo(i_index=rec.iid, index=cnt)
#    session.add(itm)
#    cnt+=1
#session.commit()
#nItms = cnt+1

# for debug, under which case userinfo is constructed

for usr in session.query(UserInfo.name, UserInfo.index).filter(UserInfo.index != None).all():
    tableUI[usr.name]=usr.index

for rec in session.query(ItemInfo.i_index, ItemInfo.index).all():
    tableII[rec.i_index]=rec.index

nUsers=session.query(UserInfo).filter(UserInfo.index!=None).count()
nItms=session.query(ItemInfo).count()

gp=dict()
gp['bias_items']=np.zeros((nItms,1))
gp['bias_users']=np.zeros((nUsers,1))
gp['bias_states']={}

gp['global_avg'] = float(session.query(func.avg(Record.rate).label('average')).\
    filter(Record.rate != None).scalar())

for q in session.query(Record.iid, func.avg(Record.rate).label('average')).\
    filter(Record.rate != None).group_by(Record.iid):
    gp['bias_items'][tableII[q.iid]]=float(q.average)-float(gp['global_avg'])

for q in session.query(Record.name, func.avg(Record.rate).label("average")).\
    filter(Record.rate != None).group_by(Record.name):
    gp['bias_users'][tableUI[q.name]]=float(q.average)-float(gp['global_avg'])

for q in session.query(Record.state, func.avg(Record.rate).label('average')).\
    filter(Record.rate != None).group_by(Record.state):
    gp['bias_states'][q.state]=float(q.average)-float(gp['global_avg'])

nFaved = session.query(Record).count()
data = np.zeros(nFaved)
i = np.zeros(nFaved)
j = np.zeros(nFaved)
idx=0
for q in session.query(Record.name, Record.iid, Record.state, Record.rate):
    if q.rate!=None:
        data[idx]=q.rate-float(gp['global_avg'])
    else:
        data[idx]=gp['bias_items'][tableII[q.iid]]+gp['bias_users'][tableUI[q.name]]+\
        gp['bias_states'][q.state]
    i[idx]=tableUI[q.name]
    j[idx]=tableII[q.iid]
    idx+=1
gp['utiliary_mtx']=sparse.coo_matrix((data,(i,j))).tolil()

fw = open('dat/mat.dat','wb')
pickle.dump(gp,fw)
pickle.dump(tableUI,fw)
pickle.dump(tableII,fw)
fw.close()