from fetch import session, Base, engine, Users, Record, UserInfo, ItemInfo
from sqlalchemy.sql.expression import func
import numpy as np

cnt=0;
for usr in session.query(Users.name).order_by(Users.uid).all():
    count = session.query(Record).filter(Record.name==usr.name).count()
    ratecount = session.query(Record).filter(Record.name==usr.name, Record.rate != None).count()
    average = session.query(func.avg(Record.rate).label('average')).\
    filter(Record.name==usr.name, Record.rate != None).scalar();
    temp = [];
    for q in session.query(Record.rate).filter(Record.name==usr.name, Record.rate != None):
        temp.append(q.rate)
    sd = np.std(temp)
    if count>0:
        if ratecount>0:
            itm = UserInfo(name=usr.name, index=cnt, count=count, ratecount=ratecount, \
            average = average, sd=sd)
        else:
            itm = UserInfo(name=usr.name, index=cnt, count=count, ratecount=ratecount)
        session.add(itm)
        cnt+=1
    else:
        itm = UserInfo(name=usr.name, count=0, ratecount=0)
        session.add(itm)
session.commit()
nUsers=cnt+1

#cnt=0;
#for rec in session.query(Record.iid).group_by(Record.iid).order_by(Record.iid).all():
#    itm = ItemInfo(i_index=rec.iid, index=cnt)
#    session.add(itm)
#    cnt+=1
#session.commit()
#nItms = cnt+1

# After that, you can check your database, and try to index some columns