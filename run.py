from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

from appF.views import *
# Importato non all'inizio per evitare dipendenze circolari

if __name__ == '__main__':
    app.run()
