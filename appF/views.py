import re

from datetime import *
import bcrypt
from flask import *
from flask_login import login_user, logout_user, login_required, current_user

from run import app, db
from appF.models import *


# insert_corso(10, 1, time(12,0,0), time(13,0,0), date.today(),"DCKDFY89H07C957C")


@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("home.html", authenticated=True)
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = bytes(request.form['password'],
                         encoding="utf-8")  # todo: controllare se è possibile .encode() chiedere a Mario
        logging = db.session.query(Persona).filter(Persona.Email == username).first()
        if logging is not None and bcrypt.checkpw(password, logging.Password.encode("utf-8")):
            user = get_persona_by_email(request.form['username'])
            login_user(user)
            return redirect(url_for('show_profile', username=user.Email))
        else:
            msg = 'Username o password non corretti'

    return render_template('login.html', msg=msg)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        registration = db.session.query(Persona).filter(Persona.Email == email).first()
        cf = db.session.query(Persona).filter(Persona.CF == request.form['Codice fiscale']).first()
        if not request.form['name'] or not request.form['surname'] or not request.form['DataNascita'] or not \
                request.form['Codice fiscale'] or not request.form['email'] or not request.form['sex'] or not \
                request.form['password']:
            msg = 'Rimpire tutto il form'
        elif registration is not None or cf is not None:
            msg = 'Persona già registrata'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Indirizzo email non valido'

        # elif not re.match(r'/^(?:[A-Z][AEIOU][AEIOUX]|[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}(?:[\dLMNP-V]{2}(?:[A-EHLMPR-T]
        # (?:[04LQ][1-9MNP-V]|[15MR][\dLMNP-V]|[26NS][0-8LMNP-U])|[DHPS][37PT][0L]|[ACELMRT][37PT][01LM]|[AC-EHLMPR-T]
        # [26NS][9V])|(?:[02468LNQSU][048LQU]|[13579MPRTV][26NS])B[26NS][9V])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L]
        # (?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$/i', CF):
        #    msg = 'Codice fiscale non valido'
        # (http://blog.marketto.it/2016/01/regex-validazione-codice-fiscale-con-omocodia/) REGEX PER CODICE FISCALE
        # TODO: testarlo

        else:
            nuova_persona = insert_persona(nome=request.form['name'], cognome=request.form['surname'],
                                           data_nascita=request.form['DataNascita'], cf=request.form['Codice fiscale'],
                                           email=request.form['email'], telefono=request.form['telefono'],
                                           sesso=request.form['sex'],
                                           password=bcrypt.hashpw(request.form['password'].encode("utf-8"),
                                                                  bcrypt.gensalt()).decode("utf-8"), attivo=False)
            if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id())
                    .filter(Staff.Ruolo == 'Gestore')).count():
                insert_istruttore(nuova_persona)
            else:
                insert_cliente(nuova_persona)
            # msg = 'Ti sei registrato con successo!' non visualizzato a causa del redirect
            login_user(nuova_persona)
            return redirect(url_for('show_profile', username=nuova_persona.Email))
    elif request.method == 'POST':
        msg = 'Riempi tutti i campi del form'

    return render_template('register.html', msg=msg)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def show_profile(username):
    msg = ""
    if not username == current_user.get_email:
        return redirect(url_for('show_profile', username=current_user.get_email, msg=msg))

    if request.method == 'POST':
        new_book = workout_book(persona=get_persona_by_email(username), data=request.form['Data'],
                                oraInizio=request.form['oraInizio'], oraFine=request.form['oraFine'],
                                sala=request.form['IDSala'], corso=request.form['IDCorso'])

        if new_book is None:
            msg = 'Errore fatale, la data scelta non è valida'
        elif not new_book.Approvata:
            msg = 'Tutto pieno, sei stato messo in coda'
        else:
            msg = 'Prenotazione effettuata con successo'

    return render_template('user_page.html', username=username, msg=msg)


@app.route('/calendar')
def calendar_view_today():
    return redirect(url_for('calendar_view', anno=datetime.today().year, mese=datetime.today().month))


@app.route('/calendar/<int:anno>/<int:mese>', methods=['GET', 'POST'])
def calendar_view(anno, mese):
    corsi = get_corsi(mese, anno)
    return render_template('calendar.html', corsi=corsi, anno=anno, mese=mese)


# TODO: da decommentare in production
'''
@app.route('/dashboard')
@login_required
def admin_dashboard():
    if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(Staff.Ruolo == 'Gestore')).count():
        return render_template('calendar.html', corsi=get_corsi(5, 2021))  # TODO: impostare mese corretto
    else:
        abort(401)
'''


@app.route("/corso/<id>")
def view_corso(id):
    corso = db.session.query(Corso).filter(Corso.IDCorso == id).first()
    istruttore = db.session.query(Persona).filter(Persona.CF == corso.IDIstruttore).first()
    return render_template('corso.html', corso=corso, istruttore=istruttore,
                           iscritti=numero_iscritti_corso(corso.IDCorso))


# TODO: da eliminare/aggiornare in production
@app.route("/dashboard")
def dashboard_view():
    return render_template('adminDashboard.html')
