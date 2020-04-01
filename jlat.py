import os, logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from db import db
from auth import Auth, login_required
from info import Info
from static import Static

toBoolean = {'true': True, 'false':False}


JLAT_PORT = int(os.environ.get('JLAT_PORT', '5000'))
JLAT_DEBUG = toBoolean.get(os.environ.get('JLAT_DEBUG', 'false'), False)
JLAT_HOST = os.environ.get('JLAT_HOST', '0.0.0.0')
JLAT_DIR = os.environ.get('JLAT_DIR', os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config["VERSION"] = "0.1.6"

# db SQLAlchemy
database_file = "sqlite:///{}".format(os.path.join(JLAT_DIR, "jlat.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
# register Auth
app.register_blueprint(Auth(url_prefix="/"))
app.config['APP_NAME'] = os.environ.get('JLAT_NAME', 'JLAT Report')
# register Info
app.register_blueprint(Info(url_prefix="/"))

# register Static
JLAT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
app.register_blueprint(Static(name="js", url_prefix="/javascripts/", path=os.path.join(JLAT_PATH, "javascripts")))
app.register_blueprint(Static(name="siimple", url_prefix="/siimple/", path=os.path.join(JLAT_PATH, "siimple")))
app.register_blueprint(Static(name="css", url_prefix="/css/", path=os.path.join(JLAT_PATH, "css")))

# register JLAT
from book import Books
app.register_blueprint(Books(url_prefix="/"))
from note import Notes
app.register_blueprint(Notes(url_prefix="/"))
from review import Reviews
app.register_blueprint(Reviews(url_prefix="/"))
from up import Ups
app.register_blueprint(Ups(url_prefix='/'))




@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    return render_template('index.html')

@app.route("/lock", methods=["GET", "POST"])
@login_required
def lock():
    return 'you are authorized'

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    with app.app_context():
        for bp in app.blueprints:
            if 'init_db' in dir(app.blueprints[bp]):
                app.blueprints[bp].init_db()
    app.logger.setLevel(logging.DEBUG)
    app.run(host=JLAT_HOST, port=JLAT_PORT, debug=JLAT_DEBUG)