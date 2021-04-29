from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://campa:1234@25.75.195.73:5432/palestra'

db = SQLAlchemy(app)
engine = create_engine('postgresql://campa:1234@25.75.195.73:5432/palestra')

from dbFunctions import getSale

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/users/<username>')
def show_profile(username):
    return f'Helo {username}'

@app.route('/sale/')
def param_page():
    a = True
    b = "ciao"
    c = [1,2,3,4,5,6]
    return render_template('sale.html', sala=getSale())
