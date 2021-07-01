from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine
from flask_qrcode import QRcode

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")

login_manager = LoginManager()
login_manager.init_app(app)


db = SQLAlchemy(app)
#engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
engine_ospite = create_engine(app.config['SQLALCHEMY_DATABASE_URI_OSPITE'], echo=True)
engine_utente = create_engine(app.config['SQLALCHEMY_DATABASE_URI_UTENTE'], echo=True)
engine_istruttore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_ISTRUTTORE'], echo=True)
engine_gestore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_GESTORE'], echo=True)


QRcode(app)

#locale.setlocale(locale.LC_ALL, 'it_IT')

from appF.views import *  # Non importato all'inizio per evitare dipendenze circolari
from appF.models import *


@login_manager.user_loader
def load_user(cf):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    q = session_ospite.query(Persona).filter(Persona.CF == cf)
    return q.first()


if __name__ == '__main__':
    app.run()
