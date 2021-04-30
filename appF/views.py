from flask import *
from run import app

from appF.models import getSale


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

