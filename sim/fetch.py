from settings import *
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql.expression import func

engine = create_engine('mysql+mysqldb://%s:%s@%s/%s?charset=utf8&use_unicode=0'%(MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST,MYSQL_DBNAME))

Base = declarative_base()

class Users(Base):
    __tablename__= 'users'

    uid = Column(Integer)
    name = Column(String(100),primary_key=True,index=True)
    joindate = Column(Date)

    def __repr__(self):
       return "<Users(uid='%s', name='%s', joindate='%s')>" % (
                self.uid, self.name, self.joindate)

class Record(Base):
    __tablename__ = 'record'

    #name = Column(String(100),primary_key=True,ForeignKey('users.name'))
    name = Column(String(100),primary_key=True,index=True)
    typ = Column(String(8),primary_key=True)
    iid = Column(Integer,primary_key=True)
    state = Column(String(20),nullable=False)
    adddate = Column(Date,nullable=False)
    rate = Column(Integer)
    comment = Column(Text)
    tags = Column(String(500))

    #user = relationship("Users",backref=backref("record"))

    def __repr__(self):
       return "<Record(name='%s', typ='%s', iid='%s')>" % (
                self.name, self.typ, self.iid)

class UserInfo(Base):
    __tablename__='userinfo'

    name = Column(String(100), primary_key=True)
    index = Column(Integer, nullable=False)
    count = Column(Integer)

    def __repr__(self):
       return "<UserInfo(name='%s', typ='%s')>" % (
                self.name, self.typ)

#UserInfo.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__=='__main__':
    print session.query(func.avg(Record.rate).label('averate')).\
        filter(Record.rate != None, Record.typ=='anime').scalar()