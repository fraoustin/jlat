from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from auth import checkAdmin, checkAuthorization

from db import db
from db.models import Book
from db.models import User
from note import NOTATION


__version__ = '0.1.0'


@login_required
@checkAuthorization('Synth','voir')
def view():
    return render_template('synth.html', books=Book.all(sortby=Book.idext), users=User.all(sortby=User.name))

class Synth(Blueprint):

    def __init__(self, name='synth', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/synth', 'synth', view, methods=['GET'])
        self.authorization = ['voir',]

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except:
            app.logger.error("init synth on register is failed")
