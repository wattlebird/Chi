from app import db

class UserInfo(db.Model):
    __tablename__ = 'userinfo'

    name = db.Column(db.String(30), primary_key=True)
    index = db.Column(db.Integer)
    count = db.Column(db.Integer)
    ratecount = db.Column(db.Integer)
    average = db.Column(db.Float)
    sd = db.Column(db.Float)

    def __repr__(self):
       return "<userinfo(name='%s')>" % (self.name)

class ItemInfo(db.Model):
    __tablename__='iteminfo'
    i_index = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)

    def __repr__(self):
        return "<ItemInfo(item_id='%s')>" % (
                self.i_index)