import numpy as np
from scipy import sparse
from fetch import session, Base, engine, Users, Record, UserInfo
from sqlalchemy.sql.expression import func
from settings import TYPE_LIST
import pickle

rateInfo = dict()
tableState = {'do':1,'collect':2,'wish':3,'on_hold':4,'dropped':5}
tableUI=dict()

nUsers = session.query(Users.uid).count()

#cnt=0;
#for usr in session.query(Users.name).all():
#    tableUI[usr.name]=cnt
#    count = session.query(Record).filter(Record.name==usr.name).count()
#    itm = UserInfo(name=usr.name, index=cnt, count=count)
 #   session.add(itm)
#    cnt+=1
#session.commit()

# for debug, under which case userinfo is constructed
for usr in session.query(UserInfo.name, UserInfo.index).all():
    tableUI[usr.name]=usr.index

for tp in TYPE_LIST:
    nItms = session.query(func.max(Record.iid)).filter(Record.typ==tp).scalar()
    gp=dict()
    gp['bias_items']=np.zeros((nItms,1))
    gp['bias_users']=np.zeros((nUsers,1))
    gp['bias_states']={}

    gp['global_avg'] = float(session.query(func.avg(Record.rate).label('averate')).\
        filter(Record.rate != None, Record.typ==tp).scalar())

    for q in session.query(Record.iid, func.avg(Record.rate).label('average')).\
        filter(Record.rate != None, Record.typ==tp).group_by(Record.iid):
        gp['bias_items'][q.iid-1]=float(q.average)-float(gp['global_avg'])

    for q in session.query(Record.name, func.avg(Record.rate).label("average")).\
        filter(Record.rate != None, Record.typ==tp).group_by(Record.name):
        idx = tableUI[q.name]
        gp['bias_users'][idx]=float(q.average)-float(gp['global_avg'])

    for q in session.query(Record.state, func.avg(Record.rate).label('average')).\
        filter(Record.rate != None, Record.typ==tp).group_by(Record.state):
        gp['bias_states'][tableState[q.state]]=float(q.average)-float(gp['global_avg'])

    nFaved = session.query(Record).filter(Record.typ==tp).count()
    data = np.zeros(nFaved)
    i = np.zeros(nFaved)
    j = np.zeros(nFaved)
    idx=0
    for q in session.query(Record.name, Record.iid, Record.state).\
        filter(Record.typ==tp):
        data[idx]=tableState[q.state]
        i[idx]=tableUI[q.name]
        j[idx]=q.iid-1
        idx+=1
    gp['state_mtx']=sparse.coo_matrix((data,(i,j))).tolil()

    nRated = session.query(Record).filter(Record.typ==tp, Record.rate!=None).count()
    data = np.zeros(nRated)
    i = np.zeros(nRated)
    j = np.zeros(nRated)
    idx=0;
    for q in session.query(Record.name, Record.iid, Record.rate, Record.state).\
        filter(Record.rate != None, Record.typ==tp):
        
        i[idx]=tableUI[q.name]
        j[idx]=q.iid-1
        data[idx]=q.rate-(float(gp['global_avg'])+gp['bias_items'][q.iid-1]+\
                  gp['bias_users'][tableUI[q.name]]+gp['bias_states'][tableState[q.state]])
        idx+=1
    gp['utiliary_mtx'] = sparse.coo_matrix((data,(i,j))).tolil()

    rateInfo[tp]=gp

fw = open('dat/mat.dat','wb')
pickle.dump(rateInfo,fw)
pickle.dump(tableState,fw)
pickle.dump(tableUI,fw)
fw.close()