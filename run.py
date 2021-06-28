from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine
import locale

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")

login_manager = LoginManager()
login_manager.init_app(app)

# TODO: CREARE CONNESSIONI DIVERSE
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com' # TODO: da configurare
app.config['MAIL_PORT'] = 465 # da configurare
app.config['MAIL_USERNAME'] = 'yourId@gmail.com' # da configurare
app.config['MAIL_PASSWORD'] = '*****' # da configurare
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True


"""
engine_ospite = create_engine(app.config['SQLALCHEMY_DATABASE_URI_OSPITE'], echo=True)
engine_utente = create_engine(app.config['SQLALCHEMY_DATABASE_URI_UTENTE'], echo=True)
engine_istruttore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_ISTRUTTORE'], echo=True)
engine_gestore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_GESTORE'], echo=True)
"""

#locale.setlocale(locale.LC_ALL, 'it_IT')

from appF.views import *  # Non importato all'inizio per evitare dipendenze circolari
from appF.models import *


@login_manager.user_loader
def load_user(cf):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    q = db.session.query(Persona).filter(Persona.CF == cf)
    return q.one()


if __name__ == '__main__':
    app.run()
