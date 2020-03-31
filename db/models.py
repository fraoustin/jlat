from flask_login import current_user
import datetime
from db import db

from auth import User

NOTATION = {'A':10,
            'Aa':9,
            'a':8,
            'aB':7,
            'B':6,
            'Bb':5,
            'b':4,
            'bC':3,
            'C':2,
            'Cd':1,
            'd':0}

INVNOTATION = {}
for note in NOTATION:
    INVNOTATION[NOTATION[note]] = note

class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idext = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    author = db.Column(db.String, nullable=True)
    year = db.Column(db.String, nullable=False)
    lastmodifiedby = db.Column(db.String, nullable=True)
    lastmodified = db.Column(db.DateTime, nullable=True)

    def __setattr__(self, name, value):
        if type(value) == str and len(value) == 0:
            value = None
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)
    
    def save(self):
        self.lastmodifiedby = current_user.name
        self.lastmodified = datetime.datetime.now()
        db.Model.save(self)
    
    @property
    def notes(self):
        return Note.query.filter_by(idbook=self.id).order_by(Note.id).all()

class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idbook = db.Column(db.Integer, nullable=False)
    iduser = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Integer, default=0)
    description = db.Column(db.String, nullable=True)
    lastmodifiedby = db.Column(db.String, nullable=True)
    lastmodified = db.Column(db.DateTime, nullable=True)
    checked = db.Column(db.Boolean, nullable=False, default=False)

    def __setattr__(self, name, value):
        if type(value) == str and len(value) == 0:
            value = None
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)
    
    def save(self):
        self.lastmodifiedby = current_user.name
        self.lastmodified = datetime.datetime.now()
        db.Model.save(self)
    
    @property
    def book(self):
        return Book.get(self.idbook)
    
    @property
    def user(self):
        return User.get(self.iduser)
    
    @property
    def onlyView(self):
        if not self.id:
            return False
        if current_user.isadmin:
            return False
        if self.checked:
            return True
        if self.iduser == current_user.id and not self.checked:
            return False
        if self.lastmodifiedby == current_user.name and not self.checked:
            return False
        return True
    
    @property
    def noteStr(self):
        return INVNOTATION.get(self.note, 'd')