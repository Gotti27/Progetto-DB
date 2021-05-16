import re

from datetime import *
from flask import *
from flask_login import login_user, logout_user

from run import app, db, login_manager, get_user_by_email
from appF.models import *


# insert_corso(10, 1, time(12,0,0), time(13,0,0), date.today(),"DCKDFY89H07C957C")


@app.route('/')
def hello_world():
    return render_template("home.html")


@app.route('/users/')
def show_profile():
    return f'Helo'


@app.route('/sale/')
def param_page():
    a = True
    b = "ciao"
    c = [1, 2, 3, 4, 5, 6]
    return render_template('sale.html', sala=getSale())


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        logging = db.session.query(Persone).filter(Persone.Email == username
                                                   and Persone.Password == password).one()
        if logging is not None:
            user = get_user_by_email(request.form['username']) # non funzionante
            login_user(user)
            return render_template('index.html')
        else:
            msg = 'Username o password non corretti'

    return render_template('login.html', msg=msg)


@app.route('/logout')
# @login_required
def logout():
    logout_user() #da rivedere, non sono sicuro
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        registration = db.session.query(Persone).filter(Persone.Email == email).first()
        cf = db.session.query(Persone).filter(Persone.CF == request.form['Codice fiscale']).first()
        if registration is not None or cf is not None:
            msg = 'Persona già registrata'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Indirizzo email non valido'

        #elif not re.match(r'/^(?:[A-Z][AEIOU][AEIOUX]|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}(?:[\dLMNP-V]{2}(?:[A-EHLMPR-T]
        # (?:[04LQ][1-9MNP-V]|[15MR][\dLMNP-V]|[26NS][0-8LMNP-U])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM]|[AC-EHLMPR-T]
        # [26NS][9V])|(?:[02468LNQSU][048LQU]|[13579MPRTV][26NS])B[26NS][9V])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L]
        # (?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$/i', CF):
        #    msg = 'Codice fiscale non valido'
        #(http://blog.marketto.it/2016/01/regex-validazione-codice-fiscale-con-omocodia/) REGEX PER CODICE FISCALE
        #TODO: testarlo

        elif not request.form['name'] or not request.form['surname'] or not request.form['DataNascita'] or not \
        request.form['Codice fiscale'] or not request.form['email'] or not request.form['sex'] or not request.form[
            'password']:
            msg = 'Rimpire tutto il form'
        else:
            # FIXME: sistemare argomenti
            insert_cliente(Nome=request.form['name'], Cognome=request.form['surname'],
                                 DataNascita=request.form['DataNascita'], CF=request.form['Codice fiscale'],
                                 Email=request.form['email'], Telefono=request.form['telefono'],
                                 Sesso=request.form['sex'], Password=request.form['password'], Attivo=False)
            msg = 'Ti sei registrato con successo!'
            # TODO: far passare alla pagina loggata dell'utente?
    elif request.method == 'POST':
        msg = 'Riempi tutti i campi del form'

    return render_template('register.html', msg=msg)


@app.route('/dashboard')
def adminDashboard():
    return render_template('adminDashboard.html', corsi=get_corsi(5, 2021))
