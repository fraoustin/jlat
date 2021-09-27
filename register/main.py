from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from auth import checkAdmin
from werkzeug.utils import secure_filename
import os
import datetime
import unidecode
import random

from db import db
from db.models import Book
from db.models import ParamRegister

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


__version__ = '0.1.0'

PARAMS = ['opened', 'year', 'head', 'foot', 'smtpurl', 'smtpemail', 'smtpemailcc', 'smtppassword', 'smtpmsg', 'smtpport', 'smtpsubject']

ALLOWED_EXTENSIONS = ['doc', 'docx', 'odt']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def inscription():
    opened = ParamRegister.getValue('opened')
    head = ParamRegister.getValue('head')
    foot = ParamRegister.getValue('foot')
    factorOne = random.randint(0, 10)
    factorTwo = random.randint(0, 10)
    return render_template('inscription.html', opened=opened, head=head, foot=foot, factorone=factorOne, factortwo=factorTwo)


def add():
    try:
        opened = ParamRegister.getValue('opened')
        if opened != 'on':
            flash("Le concours n'est pas ouvert", 'warning')
            raise ValueError('is not opened')
        if int(request.form['factorone'])*int(request.form['factortwo']) != int(request.form['captcha']):
            flash("Il y a une erreur dans votre multiplication", 'warning')
            raise ValueError('captcha')
        if len(request.form['email']) == 0:
            flash('Vous devez ajouter votre email', 'warning')
            raise ValueError('no email')
        if 'file' not in request.files:
            flash('Vous devez ajouter votre fichier', 'warning')
            raise ValueError('no file')
        file = request.files['file']
        if file.filename == '':
            flash('Vous devez ajouter votre fichier', 'warning')
            raise ValueError('no file')
        if file and allowed_file(file.filename) is False:
            flash('Votre fichier n\'a pas le bon format', 'warning')
            raise ValueError('no file')
        title = request.form['title']
        author = request.form['lastname'] + ' ' + request.form['firstname']
        year = ParamRegister.getValue('year')
        email = ';'.join(request.form['email'].strip().split(' '))
        phone = request.form['phone']
        nationality = request.form['nationality']
        address = request.form['address']
        trad_lastname = request.form['trad_lastname']
        trad_firstname = request.form['trad_firstname']
        trad_email = request.form['trad_email']
        trad_phone = request.form['trad_phone']
        trad_nationality = request.form['trad_nationality']
        trad_address = request.form['trad_address']
        description = request.form['description']
        
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            pathfile = os.path.join(current_app.config['BOOK_FOLDER'], datetime.datetime.now().strftime('%Y%m%d%H%M%S') + unidecode.unidecode(filename))
            file.save(pathfile)
            fileurl = '/uploads' + pathfile.split('/uploads')[1]
        
        books = Book.all(sortby=Book.idext)
        if len(books) == 0:
            idext = '0001'
        else:
            idext = '{:0>4}'.format(str(int(books[-1].idext)+1))
        book = Book(title=title, 
            author=author,
            year=year,
            email=email,
            phone=phone,
            nationality=nationality,
            address=address,
            fileurl=fileurl,
            trad_lastname=trad_lastname,
            trad_firstname=trad_firstname,
            trad_email=trad_email,
            trad_phone=trad_phone,
            trad_nationality=trad_nationality,
            trad_address=trad_address,
            description=description,
            idext=idext)
        book.save()
        send_mail(book)
        flash('Votre inscription est validée, vous allez recevoir un mail', 'info')
        return redirect(request.url)
    except Exception as err:
        current_app.logger.error(err)
        flash('Votre inscription n\'est pas validée', 'error')
        return redirect(request.url)


def send_mail(book):
    Fromadd = ParamRegister.getValue('smtpemail')
    to = []
    if len(book.email) > 0:
        to.append(book.email)
    if len(book.trad_email) > 0:
        to.append(book.trad_email)
    Toadd = ",".join(to)
    bcc = ParamRegister.getValue('smtpemail')
    message = MIMEMultipart()
    message['From'] = Fromadd
    message['To'] = Toadd
    message['BCC'] = bcc
    message['Subject'] = ParamRegister.getValue('smtpsubject')
    message.attach(MIMEText(ParamRegister.getValue('smtpmsg')))
    serveur = smtplib.SMTP(ParamRegister.getValue('smtpurl'), int(ParamRegister.getValue('smtpport')))
    serveur.starttls()
    serveur.login(Fromadd, ParamRegister.getValue('smtppassword'))
    serveur.sendmail(Fromadd, Toadd.split(','), message.as_string())
    serveur.quit()

@login_required
@checkAdmin()
def register():
    params = {}
    for param in PARAMS:
        params[param] = ParamRegister.getValue(param)
    return render_template('register.html', **params)


@login_required
@checkAdmin()
def update():
    for param in PARAMS:
        paramregister = ParamRegister.get(param)
        paramregister.value = request.form.get(param,'')
        paramregister.save()
    return redirect(url_for('register.register'))
    

class Register(Blueprint):
    def __init__(self, name='register', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/register', 'register', register, methods=['GET'])
        self.add_url_rule('/register', 'update_register', update, methods=['POST'])
        self.add_url_rule('/inscription', 'inscription', inscription, methods=['GET'])
        self.add_url_rule('/inscription', 'add_inscription', add, methods=['POST'])
        
    def init_db(self):
        for param in PARAMS:
            if ParamRegister.get(param) is None:
                db.session.add(ParamRegister(key=param, value=''))
                db.session.commit()
                current_app.logger.info("create param register %s" % param)

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except:
            app.logger.error("init register on register is failed")