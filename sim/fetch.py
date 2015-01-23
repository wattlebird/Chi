from settings import *
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql.expression import func

engine = create_engine('mysql+mysqldb://%s:%s@%s/%s?charset=utf8&use_unicode=0'%(MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST,MYSQL_DBNAME))

Base = declarative_base()

class Users(Base):
    __tablename__= 'users'

    uid = Column(Integer,nullable=False)
    name = Column(String(30),primary_key=True,index=True)
    joindate = Column(Date,nullable=False)

    def __repr__(self):
       return "<Users(uid='%s', name='%s', joindate='%s')>" % (
                self.uid, self.name, self.joindate)

class Record(Base):
    __tablename__ = 'record'

    #name = Column(String(100),primary_key=True,ForeignKey('users.name'))
    name = Column(String(30),primary_key=True,index=True)
    typ = Column(String(5),primary_key=True)
    iid = Column(Integer,primary_key=True)
    state = Column(String(7),nullable=False)
    adddate = Column(Date,nullable=False)
    rate = Column(Integer)
    comment = Column(String(401))
    tags = Column(String(401))

    #user = relationship("Users",backref=backref("record"))

    def __repr__(self):
       return "<Record(name='%s', iid='%s')>" % (
                self.name, self.iid)

class UserInfo(Base):
    __tablename__='userinfo'

    name = Column(String(30), primary_key=True)
    index = Column(Integer)
    count = Column(Integer)

    def __repr__(self):
       return "<UserInfo(name='%s')>" % (
                self.name)

class ItemInfo(Base):
    __tablename__='iteminfo'
    i_index = Column(Integer, primary_key=True)
    index = Column(Integer)

    def __repr__(self):
        return "<ItemInfo(item_id='%s')>" % (
                self.i_index)

#UserInfo.__table__.drop(engine, checkfirst=True)
#ItemInfo.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__=='__main__':
    print session.query(func.avg(Record.rate).label('averate')).\
        filter(Record.rate != None, Record.typ=='anime').scalar()