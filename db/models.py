from flask_login import current_user
import datetime
from db import db

from auth import User

NOTATION = {'A':9,
            'Aa':8,
            'a':7,
            'aB':6,
            'B':5,
            'Bb':4,
            'b':3,
            'bC':2,
            'C':1}

NOTATIONTOAVG = {9:20,
                8:18,
                7:15,
                6:12,
                5:10,
                4:8,
                3:5,
                2:2,
                1:0}

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
    onrace = db.Column(db.Boolean, nullable=False, default=True)

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
    
    @property
    def onraceStr(self):
        if self.onrace:
            return "oui"
        return "non"
    
    @property
    def average(self):
        notes = self.notes
        if len(notes) < 2:
            return False
        return round(sum([ NOTATIONTOAVG.get(note.note,0) for note in notes]) / len(notes), 1)
    
    def getNoteFrom(self, iduser):
        note = Note.query.filter_by(idbook=self.id, iduser=iduser).first()
        if note is None:
            return ""
        return note.noteStr

class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idbook = db.Column(db.Integer, nullable=False)
    iduser = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Integer, default=1)
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