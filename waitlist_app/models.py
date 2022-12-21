from . import db

class WaitList(db.Model):
    __tablename__ = 'wait_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    entries = db.relationship("WaitListEntry", cascade="all, delete-orphan", back_populates="wait_list", primaryjoin="WaitList.id==WaitListEntry.wait_list_id")

class WaitListEntry(db.Model):
    __tablename__ = 'wait_list_entries'
    id = db.Column(db.Integer, primary_key=True)
    wait_list_id = db.Column(db.Integer, db.ForeignKey('wait_lists.id'))
    name = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    rank = db.Column(db.Integer)
    wait_list = db.relationship("WaitList", back_populates="entries")
