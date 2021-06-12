import os
import logging
from shutil import copyfile, rmtree

from flask import Blueprint, render_template, current_app, send_from_directory, redirect, request
from flask_login import login_required, current_user

from static.main import add_path
from auth import checkAdmin

from db import db
from db.models import Book
from db.models import Note
from db.models import User
from note import NOTATION


@login_required
def history(path=''):
    return render_template('history.html', historys=os.listdir(path))


@login_required
@checkAdmin()
def addhistory(path=''):
    year = Book.all(sortby=Book.id)[0].year
    year_path = os.path.join(path, year)
    if os.path.isdir(year_path) is True:
        logging.info('delete %s' % year_path)
        rmtree(year_path)
    current_app.logger.info('create %s' % year_path)
    os.mkdir(year_path)
    current_app.logger.info('backup %s' % current_app.config["SQLALCHEMY_DATABASE_URI"][10:])
    copyfile(current_app.config["SQLALCHEMY_DATABASE_URI"][10:], os.path.join(year_path, 'jlat.db'))
    current_app.logger.info('write index for %s' % year)
    with open(os.path.join(year_path, "index.html"), "w") as index:
        index.write(render_template('archive_index.html', year=year))
    current_app.logger.info('write reviews for %s' % year)
    with open(os.path.join(year_path, "reviews.html"), "w") as review:
        review.write(render_template('archive_reviews.html', year=year, books=Book.all(sortby=Book.idext)))
    current_app.logger.info('write synth for %s' % year)
    with open(os.path.join(year_path, "synth.html"), "w") as synth:
        synth.write(render_template('archive_synth.html', year=year, books=Book.all(sortby=Book.idext), users=User.all(sortby=User.name)))
    return redirect('/history')


@login_required
def static_web(filename, path='..'):
    """
    return filename in path
    redirect for index.html
    """
    if filename == "index.html":
        return redirect(request.url[:-1 * len('index.html')])
    return send_from_directory(path,filename)


class History(Blueprint):
    def __init__(self, name='history', import_name=__name__, archives="./archives", *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.archives_path = os.path.abspath(archives)
        self.add_url_rule('/history', 'history', add_path(self.archives_path)(history), methods=['GET'])
        self.add_url_rule('/addhistory', 'addhistory', add_path(self.archives_path)(addhistory), methods=['GET'])
        if os.path.isfile(self.archives_path) is False:
            if os.path.isdir(self.archives_path) is False:
                try:
                    os.mkdir(self.archives_path)
                except Exception as err:
                    logging.error("no possible to create %s" % self.archives_path)
                    raise err
        else:
            raise ValueError("no possible to create %s" % self.archives_path)
        
        self.add_url_rule('/archives/<path:filename>', 'static_web', add_path(self.archives_path)(static_web))

    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init history on register is failed")