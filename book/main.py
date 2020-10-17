from flask import Blueprint, flash, request, render_template, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import datetime
from auth import checkAdmin
import unidecode

from werkzeug.utils import secure_filename
import os

from db import db
from db.models import Book

getBool ={'on': True, 'off': False}

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
    return render_template('book.html', book=Book(onrace=True))


@login_required
@checkAdmin()
def create():
    title = request.form['title']
    idext = request.form['idext']
    description = request.form['description']
    author = request.form['author']
    year = request.form['year']
    onrace = getBool.get(request.form.get('onrace','off'),False)
    email = request.form['email']
    phone = request.form['phone']
    nationality = request.form['nationality']
    address = request.form['address']
    trad_lastname = request.form['trad_lastname']
    trad_firstname = request.form['trad_firstname']
    trad_email = request.form['trad_email']
    trad_phone = request.form['trad_phone']
    trad_nationality = request.form['trad_nationality']
    trad_address = request.form['trad_address']

    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
        file.save(pathfile)
        fileurl = '/uploads' + pathfile.split('/uploads')[1]
    
    filep = request.files['filep']
    if filep:
        filename = secure_filename(file.filename)
        pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
        filep.save(pathfile)
        filepdf = '/uploads' + pathfile.split('/uploads')[1]
    
    fileu = request.files['fileu']
    if fileu:
        filename = secure_filename(file.filename)
        pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
        fileu.save(pathfile)
        fileepub = '/uploads' + pathfile.split('/uploads')[1]

    book = Book(title=title, 
        description=description,
        author=author,
        year=year,
        idext=idext,
        onrace=onrace,
        email=email,
        phone=phone,
        nationality=nationality,
        address=address,
        fileurl=fileurl,
        filepdf=filepdf,
        fileepub=fileepub,
        trad_lastname=trad_lastname,
        trad_firstname=trad_firstname,
        trad_email=trad_email,
        trad_phone=trad_phone,
        trad_nationality=trad_nationality,
        trad_address=trad_address)
    book.save()
    flash('Book "%s" is created' % title, 'success')
    return redirect(url_for('book.view_book', id=book.id))


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
        book.onrace = getBool.get(request.form.get('onrace','off'),False)
        book.email = request.form['email']
        book.phone = request.form['phone']
        book.nationality = request.form['nationality']
        book.address = request.form['address']
        book.trad_lastname = request.form['trad_lastname']
        book.trad_firstname = request.form['trad_firstname']
        book.trad_email = request.form['trad_email']
        book.trad_phone = request.form['trad_phone']
        book.trad_nationality = request.form['trad_nationality']
        book.trad_address = request.form['trad_address'] 
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
            file.save(pathfile)
            book.fileurl = '/uploads' + pathfile.split('/uploads')[1]
    
        filep = request.files['filep']
        if filep:
            filename = secure_filename(filep.filename)
            pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
            filep.save(pathfile)
            book.filepdf = '/uploads' + pathfile.split('/uploads')[1]
        
        fileu = request.files['fileu']
        if fileu:
            filename = secure_filename(fileu.filename)
            pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
            fileu.save(pathfile)
            book.fileepub = '/uploads' + pathfile.split('/uploads')[1]
        book.save()
        flash('Book "%s" is saved' % book.title,'success')
        return redirect(url_for('book.view_book', id=book.id))
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
    return render_template("books.html", books=Book.all(sortby=Book.idext))


@login_required
def static_web_uploads(filename):
    """
    return filename in path BOOK_FOLDER
    """
    current_app.logger.info(current_app.config['BOOK_FOLDER'][:-4])
    current_app.logger.info(filename)
    return send_from_directory(current_app.config['BOOK_FOLDER'][:-4],filename)



class Books(Blueprint):

    def __init__(self, name='book', import_name=__name__, dir_books="./files/uploads/book", *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.before_app_first_request(self._init)
        self.dir_books = dir_books
        self.add_url_rule('/book/<int:id>', 'view_book', view, methods=['GET'])
        self.add_url_rule('/book', 'new_book', new, methods=['GET'])
        self.add_url_rule('/book', 'create_book', create, methods=['POST'])
        self.add_url_rule('/book/<int:id>', 'update_book', update, methods=['POST'])
        self.add_url_rule('/delbook/<int:id>', 'delete_book', delete, methods=['POST'])
        self.add_url_rule('/books', 'books', list, methods=['GET'])
        self.add_url_rule('/uploads/<path:filename>', 'static_web', static_web_uploads)

    def register(self, book, options, first_registration=False):
        try:
            Blueprint.register(self, book, options, first_registration)
        except:
            book.logger.error("init book on register is failed")

    def _init(self):
        current_app.config['BOOK_FOLDER'] = self.dir_books
        if not os.path.isdir(current_app.config['BOOK_FOLDER']):
            os.makedirs(current_app.config['BOOK_FOLDER'], exist_ok=True)
