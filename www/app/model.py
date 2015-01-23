from app import db

class UserInfo(db.Model):
    __tablename__ = 'userinfo'

    name = Column(String(30), primary_key=True)
    index = Column(Integer)
    count = Column(Integer)

    def __repr__(self):
       return "<userinfo(name='%s')>" % (self.name)

