from flask import Blueprint, flash, request, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

import csv
from werkzeug.utils import secure_filename
import os

from auth import checkAdmin, User

from db import db
from db.models import Book
from db.models import Note
from note import NOTATION


ALLOWED_EXTENSIONS = ['csv',]
HEADERS = {
    'User': ['id','name','email','isadmin','gravatar'],
    'Book' : ['id','title','author','idext','year']
}
                
LABEL_HEADER = [[i, ', '.join(HEADERS[i]) ] for i in HEADERS ]

@login_required
@checkAdmin()
def view():
    return render_template('up.html', tables=['User','Book'], headers=LABEL_HEADER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def equallist(lstOne, lstTwo):
    if len(list(set(lstOne))) == len(list(set(lstTwo))):
        for i in lstOne:
            if i not in lstTwo:
                return False
        return True
    else:
        return False

def getObj(table, headers):
    if table == "User" and equallist(headers, ['id','name','email','isadmin','gravatar']):
        return User
    if table == "Book" and equallist(headers, ['id','title','author','idext','year']):
        return Book
    return None
    

@login_required
@checkAdmin()
def upload():
    table = request.form['table']
    if not len(table):
        flash('Selected table', 'error')
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pathfile = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(pathfile)
        with open(pathfile, "r") as f:
            reader = csv.DictReader(f, delimiter=";")
            obj = getObj(table, reader.fieldnames)
            if obj != None:
                number_line = 0
                try:
                    for line in reader:
                        if len(str(line['id'])):
                            elt = obj.get(line['id'])
                            if elt == None:
                                raise Exception('elt not exist')
                        else:
                            elt = obj()
                        for li in [li for li in line if line != 'id']:
                            elt.__setattr__(li, line[li])
                        elt.save()
                        number_line = number_line+1
                    flash('Import data Ok','success')
                except Exception as err :
                    print(err)
                    flash('Error import data line %s' % number_line,'error')
            else:
                flash('file does not compatible with %s' % table, 'error')
    return redirect(request.url)


class Ups(Blueprint):

    def __init__(self, name='up', import_name=__name__,dir_uploads="./uploads", *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.before_app_first_request(self._init)
        self.dir_uploads = dir_uploads
        self.add_url_rule('/up', 'up', view, methods=['GET'])
        self.add_url_rule('/up', 'upload', upload, methods=['POST'])

    def _init(self):
        current_app.config['UPLOAD_FOLDER'] = self.dir_uploads
        if not os.path.isdir(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

    def register(self, book, options, first_registration=False):
        try:
            Blueprint.register(self, book, options, first_registration)
        except:
            book.logger.error("init book on register is failed")
