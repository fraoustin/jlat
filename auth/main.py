from flask import Blueprint, current_app, flash, request, render_template, redirect, url_for
import uuid
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import hashlib

from db import db
from db.models import User

getBool ={'on': True, 'off': False}

class checkAdmin(object):

    def __call__(self, fn):
        def wrapped_f(*args, **kwargs):
            if current_user.isadmin :
                return fn(*args, **kwargs)
            flash('You are not admin', 'error')
            return redirect("/")
        return wrapped_f

@login_required
def currentuser():
    return render_template('user.html', user=current_user, backurl=None)

@login_required
def view_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user is not None:
            return render_template('user.html', user=user, backurl="/users")
        else:
            raise('user not found')
    except:
        flash('Not user identified', 'error')
        return render_template('user.html', user=current_user, backurl=None)


@login_required
@checkAdmin()
def new_user():
    return render_template('user.html', user=User(), backurl="/users")


@login_required
@checkAdmin()
def create_user():
    backurl = request.form.get('backurl','/')
    user = User()
    user.email = request.form['email']
    password = request.form['password']
    if len(password) == 0:
        password = str(uuid.uuid4())
    apikey = request.form['apikey']
    if len(apikey) == 0:
        apikey = str(uuid.uuid4())
    token = request.form['token']
    if len(token) == 0:
        token = str(uuid.uuid4())
    user.password=password
    user.apikey=apikey
    user.token=token
    user.name = request.form['name']
    user.isadmin = getBool.get(request.form.get('isadmin','off'),False)
    user.gravatar = getBool.get(request.form.get('gravatar','off'),False)
    user.save()
    flash('User %s is created' % user.name,'success')
    return redirect(backurl)


@login_required
def update_user(id):
    backurl = request.form.get('backurl','/')
    user = User.query.filter_by(id=id).first()
    if user is not None:
        user.email = request.form['email']
        user.name = request.form['name']
        if len(request.form['password']):
            user.password = request.form['password']
        apikey = request.form['apikey']
        if len(apikey) == 0:
            apikey = str(uuid.uuid4())
        token = request.form['token']
        if len(token) == 0:
            token = str(uuid.uuid4())
        user.apikey=apikey
        user.token=token
        if current_user.isadmin and current_user.id != user.id:
            user.isadmin = getBool.get(request.form.get('isadmin','off'),False)
        user.gravatar = getBool.get(request.form.get('gravatar','off'),False)
        user.save()
        flash('User is saved','success')
        return redirect(backurl)
    else:
        flash('User doesn\'t exist','warning')
        return redirect(backurl)


@login_required
@checkAdmin()
def delete_user(id):
    backurl = request.form.get('backurl','/')
    user = User.query.filter_by(id=id).first()
    if user.id == current_user.id:
        flash('You can not delete yourself','warning')
        return redirect(backurl)
    if user is not None:
        name = user.name
        user.remove()
        flash('User %s is deleted' % name,'error')
    return redirect(backurl)


@login_required
@checkAdmin()
def users():
    return render_template("users.html", users=User.all(sortby=User.name), backurl=None)


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            user.lastconnection = datetime.date.today()
            db.session.commit()
            login_user(user, remember = True)            
            return redirect(url_for('home'))
        else:
            flash('User or password is wrong','error')
            return render_template('login.html')        
    return render_template('login.html')


def logout():
    logout_user()
    return redirect(url_for('home'))


class Auth(Blueprint):

    def __init__(self, name='auth', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.before_app_first_request(self._init)
        self.add_url_rule('/logout', 'logout', logout, methods=['GET'])
        self.add_url_rule('/login', 'login', login, methods=['POST', 'GET'])
        self.add_url_rule('/currentuser', 'currentuser', currentuser, methods=['GET'])
        self.add_url_rule('/user/<int:id>', 'view_user', view_user, methods=['GET'])
        self.add_url_rule('/user', 'new_user', new_user, methods=['GET'])
        self.add_url_rule('/user', 'create_user', create_user, methods=['POST'])
        self.add_url_rule('/user/<int:id>', 'update_user', update_user, methods=['POST'])
        self.add_url_rule('/deluser/<int:id>', 'delete_user', delete_user, methods=['POST'])
        self.add_url_rule('/users', 'users', users, methods=['GET'])
        

    def _init(self):
        current_app.logger.debug("init auth on first request")
        self._login_manager = LoginManager()
        self._login_manager.init_app(current_app)
        if not current_app.secret_key:
            current_app.secret_key = str(uuid.uuid4())
            current_app.logger.warning("not secret key for app, generate secret key")

        @self._login_manager.user_loader
        def user_loader(id):
            return User.query.get(id)
        
        @self._login_manager.unauthorized_handler
        def unauthorized():
            return redirect(url_for('auth.login'))

        @self._login_manager.request_loader
        def load_user_from_request(request):
            # first, try to login using the api_key url arg
            apikey = request.args.get('api')
            if apikey:
                user = User.query.filter_by(apikey=apikey).first()
                if user is not None:
                    return user

            # next, try to login using Basic Auth
            token = request.headers.get('Authorization')
            if token:
                token = token.replace('Basic ', '', 1)
                try:
                    token = base64.b64decode(token)
                except Exception:
                    pass
                user = User.query.filter_by(token=token).first()
                if user is not None:
                    return user

            # finally, return None if both methods did not login the user
            return None
        
    def init_db(self):    
        if len(User.query.all()) == 0:
            u = User(email='admin@localhost', name="Admin", password="admin", isadmin=True)
            db.session.add(u)
            db.session.commit()
            current_app.logger.info("create user admin@localhost")
        else:
            current_app.logger.debug("we have least one user")
       
    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init auth on register is failed")