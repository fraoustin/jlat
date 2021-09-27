from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from auth import checkAdmin

from db import db
from db.models import Book
from db.models import Note
from note import NOTATION


__version__ = '0.1.0'


@login_required
def view():
    return render_template('reviews.html', books=Book.all(sortby=Book.idext))

@login_required
@checkAdmin()
def valid(id):
    note = Note.get(id=id)
    note.checked = True
    note.save()
    return "ok"

@login_required
@checkAdmin()
def onrace(id):
    book = Book.get(id)
    book.onrace = not book.onrace
    book.save()
    return "ok"

class Reviews(Blueprint):

    def __init__(self, name='review', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/reviews', 'reviews', view, methods=['GET'])
        self.add_url_rule('/note/valid/<int:id>', 'valid_note', valid, methods=['GET'])
        self.add_url_rule('/note/onrace/<int:id>', 'onrace_book', onrace, methods=['GET'])

    def register(self, review, options):
        try:
            Blueprint.register(self, review, options)
        except:
            book.logger.error("init review on register is failed")
