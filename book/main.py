from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import datetime
from auth import checkAdmin

from db import db
from db.models import Book

@login_required
def view(id):
    try:
        book = Book.get(id=id)
        if book is not None:
            return render_template('book.html', book=book)
        else:
            raise('book not found')
    except:
        flash('Not found book', 'warning')
        return redirect(url_for('books'))
        
@login_required
@checkAdmin()
def new():
    return render_template('book.html', book=Book())


@login_required
@checkAdmin()
def create():
    title = request.form['title']
    idext = request.form['idext']
    description = request.form['description']
    author = request.form['author']
    year = request.form['year']
    book = Book(title=title, description=description, author=author, year=year, idext=idext)
    book.save()
    flash('Book "%s" is created' % title, 'success')
    return redirect(url_for('book.update_book', id=book.id))


@login_required
@checkAdmin()
def update(id):
    book = Book.get(id=id)
    if book is not None:
        book.title = request.form['title']
        book.description = request.form['description']
        book.author = request.form['author']
        book.year = request.form['year']
        book.idext = request.form['idext']
        book.save()
        flash('Book "%s" is saved' % book.title,'success')
        return redirect(url_for('book.update_book', id=book.id))
    else:
        flash('Book doesn\'t exist','error')
        return redirect(url_for('book.books'))

@login_required
@checkAdmin()
def delete(id):
    book = Book.get(id=id)
    if book is not None:
        title = book.title
        book.remove()
        flash('Book "%s" is deleted' % title,'error')
    return redirect(url_for('book.books'))

@login_required
def list():
    return render_template("books.html", books=Book.all(sortby=Book.title))


class Books(Blueprint):

    def __init__(self, name='book', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/book/<int:id>', 'view_book', view, methods=['GET'])
        self.add_url_rule('/book', 'new_book', new, methods=['GET'])
        self.add_url_rule('/book', 'create_book', create, methods=['POST'])
        self.add_url_rule('/book/<int:id>', 'update_book', update, methods=['POST'])
        self.add_url_rule('/delbook/<int:id>', 'delete_book', delete, methods=['POST'])
        self.add_url_rule('/books', 'books', list, methods=['GET'])

    def register(self, book, options, first_registration=False):
        try:
            Blueprint.register(self, book, options, first_registration)
        except:
            book.logger.error("init book on register is failed")
