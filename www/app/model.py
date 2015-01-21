from app import db

class UserInfo(db.Model):
    __tablename__ = 'userinfo'

    name = Column(String(100), primary_key=True)
    index = Column(Integer, nullable=False)
    count = Column(Integer)

    def __repr__(self):
       return "<userinfo(name='%s')>" % (self.name)

