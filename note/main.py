from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import datetime

from db import db

from db.models import Book
from db.models import Note
from db.models import NOTATION

from auth import User, checkAuthorization


__version__ = '0.1.0'


getBool ={'on': True, 'off': False}

@login_required
@checkAuthorization('Notes','voir')
def view(id):
    try:
        note = Note.get(id=id)
        if note is not None:
            return render_template('note.html', note=note, users=User.all(sortby=User.name), books=Book.all(sortby=Book.title), notation=NOTATION)
        else:
            raise('note not found')
    except:
        flash('Not found note', 'warning')
        return redirect(url_for('notes'))
        
@login_required
@checkAuthorization('Notes','ajouter modifier')
def new():
    return render_template('note.html', note=Note(), users=User.all(sortby=User.name), books=Book.all(sortby=Book.title), notation=NOTATION)


@login_required
@checkAuthorization('Notes','ajouter modifier')
def create():
    idbook = request.form['idbook']
    iduser = request.form['iduser']
    note = Note.query.filter_by(idbook=idbook, iduser=iduser).first()
    if note is None:
        note = Note(idbook=idbook, iduser=iduser)
    note.checked = getBool.get(request.form.get('checked','off'),False)
    note.note = request.form['note']
    note.description = request.form['description']
    note.save()
    flash('Note is created', 'success')
    return redirect(url_for('note.view_note', id=note.id))


@login_required
@checkAuthorization('Notes','ajouter modifier')
def update(id):
    note = Note.get(id=id)
    if note is not None:
        note.idbook = request.form['idbook']
        note.iduser = request.form['iduser']
        note.note = request.form['note']
        note.description = request.form['description']
        note.checked = getBool.get(request.form.get('checked','off'),False)
        note.save()
        flash('Note is saved', 'success')
        return redirect(url_for('note.view_note', id=note.id))
    else:
        flash('Note doesn\'t exist','error')
        return redirect(url_for('note.notes'))

@login_required
@checkAuthorization('Notes','supprimer')
def delete(id):
    note = Note.get(id=id)
    if note is not None:
        note.remove()
        flash('Note is deleted','error')
    return redirect(url_for('note.notes'))

@login_required
@checkAuthorization('Notes','voir')
def listing():
    return render_template("notes.html", notes=sorted(Note.all(), key=lambda note: note.book.idext))

@login_required
@checkAuthorization('Notes','note rapide')
def wizardnoteview():
    return render_template("wizardnote.html", users=User.all(sortby=User.name), books=Book.all(sortby=Book.idext), notation=NOTATION)

@login_required
@checkAuthorization('Notes','note rapide')
def wizardnotecreate():
    idbook = request.form['idbook']
    iduser = request.form['iduser']
    note = Note.query.filter_by(idbook=idbook, iduser=iduser).first()
    if note is None:
        note = Note(idbook=idbook, iduser=iduser)
    note.note = request.form['note']
    note.description = request.form['description']
    note.save()
    flash('Note is created', 'success')
    return redirect(url_for('home'))


@login_required
def getdescription(idbook, iduser):
    note = Note.query.filter_by(idbook=idbook, iduser=iduser).first()
    if note is None:
        return ""
    return note.description

class Notes(Blueprint):

    def __init__(self, name='note', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/note/<int:id>', 'view_note', view, methods=['GET'])
        self.add_url_rule('/note', 'new_note', new, methods=['GET'])
        self.add_url_rule('/note', 'create_note', create, methods=['POST'])
        self.add_url_rule('/note/<int:id>', 'update_note', update, methods=['POST'])
        self.add_url_rule('/delnote/<int:id>', 'delete_note', delete, methods=['POST'])
        self.add_url_rule('/notes', 'notes', listing, methods=['GET'])
        self.add_url_rule('/wizardnote', 'wizard_note', wizardnoteview, methods=['GET'])
        self.add_url_rule('/wizardnote', 'wizard_new_note', wizardnotecreate, methods=['POST'])
        self.add_url_rule('/note/description/<int:idbook>/<int:iduser>', 'description_note', getdescription, methods=['GET'])
        self.authorization = ['note rapide', 'voir', 'ajouter modifier', 'supprimer']

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except:
            app.logger.error("init note on register is failed")
