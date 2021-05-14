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


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = "HELO"
    '''
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    '''

    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    '''
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
    '''
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    '''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    '''
    return render_template('register.html', msg=msg)


@app.route('/dashboard')
def adminDashboard():
    return render_template('adminDashboard.html')