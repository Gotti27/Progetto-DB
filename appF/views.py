from flask import *
from run import app

from appF.models import *


@app.route('/')
def hello_world():
    return render_template("sale.html")


@app.route('/users/')
def show_profile():
    addTestPersona()
    return f'Helo'


@app.route('/sale/')
def param_page():
    a = True
    b = "ciao"
    c = [1,2,3,4,5,6]
    return render_template('sale.html', sala=getSale())

