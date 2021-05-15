from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy import create_engine

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")

login_manager = LoginManager()
login_manager.init_app(app)

# TODO: CREARE CONNESSIONI DIVERSE
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

"""
engine_ospite = create_engine(app.config['SQLALCHEMY_DATABASE_URI_OSPITE'], echo=True)
engine_utente = create_engine(app.config['SQLALCHEMY_DATABASE_URI_UTENTE'], echo=True)
engine_istruttore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_ISTRUTTORE'], echo=True)
engine_gestore = create_engine(app.config['SQLALCHEMY_DATABASE_URI_GESTORE'], echo=True)
"""


class User(UserMixin):
    def __init__(self, id, email, pwd, role):
        self.id = id
        self.email = email
        self.pwd = pwd
        self.role = role


def get_user_by_email(username):
    user = db.session.query(User).filter_by(email=username)
    return User(user.id, user.email, user.pwd, user.role)


@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(User).filter_by(id=user_id)
    return User(user.id, user.email, user.pwd, user.role)


from appF.views import *  # Non importato all'inizio per evitare dipendenze circolari

if __name__ == '__main__':
    app.run()
