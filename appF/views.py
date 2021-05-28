import re
import time
import bcrypt
from flask import *
from flask_login import login_user, logout_user, login_required, current_user
from run import app, db
from appF.models import *


@app.route('/')
def home():
    get_time_step()
    if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(Staff.Ruolo == 'Gestore')).count():
        return render_template("home.html", current_user=current_user, admin=True)
    else:
        return render_template("home.html", current_user=current_user, admin=False)


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
            if (db.session.query(Staff).filter(Staff.IDStaff == user.get_id()).filter(Staff.Ruolo == 'Gestore')).count():
                return redirect(url_for('dashboard_view'))
            else:
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
    if current_user.is_authenticated:
        return redirect(url_for('show_profile', username=current_user.get_email))
    else:
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
                if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(Staff.Ruolo == 'Gestore')).count():
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
        is_active = db.session.query(Persona.Attivo).filter(Persona.Email == current_user.get_email).first()
        new_book = insert_prenotazione(persona=get_persona_by_email(username), data=request.form['Data'],
                                       ora_inizio=request.form['oraInizio'], ora_fine=request.form['oraFine'],
                                       sala=request.form['IDSala'], corso=request.form['IDCorso'])

        if new_book is None:
            msg = 'Errore fatale, la data scelta non è valida'
        elif not is_active:
            #todo: messaggio provvisorio
            msg = 'Non sei ancora autorizzato ad accedere alla palestra,' \
                  'la tua prenotazione è registrata ma è in attesa di validazione, ' \
                  'contatta il gestore per essere abilitato'
        elif not new_book.Approvata:
            msg = 'Tutto pieno, sei stato messo in coda'
        else:
            msg = 'Prenotazione effettuata con successo'

    return render_template('user_page.html', persona=get_persona_by_email(username), username=username, msg=msg)


@app.route('/calendar')
def calendar_view_today():
    return redirect(url_for('calendar_view', anno=datetime.today().year, mese=datetime.today().month))


@app.route('/calendar/<int:anno>/<int:mese>', methods=['GET', 'POST'])
def calendar_view(anno, mese):
    corsi = get_corsi(mese, anno)
    return render_template('calendar.html', corsi=corsi, anno=anno, mese=mese)


@app.route("/corsi")
def lista_corsi():
    lista_corsi = db.session.query(Corso).filter(Corso.Data >= date.today()).filter(Corso.OraInizio > time()).all()
    return render_template('corsi.html', lista_corsi=lista_corsi)


@app.route("/corso/<id>", methods=['GET', 'POST'])
def view_corso(id):
    corso = db.session.query(Corso).filter(Corso.IDCorso == id).first()
    istruttore = db.session.query(Persona).filter(Persona.CF == corso.IDIstruttore).first()

    if request.method == 'POST':
        if current_user.is_authenticated:
            insert_prenotazione(current_user, corso.Data, corso.OraInizio, corso.OraFine, corso.IDSala, corso.IDCorso)
            # TODO: gestire eventuali messaggi per mancata disponibilità ecc..
        # else:
            # TODO: implemetare redirect to login e redirect back

    return render_template('corso.html', corso=corso, istruttore=istruttore, iscritti=numero_iscritti_corso(corso.IDCorso))


# TODO: usare in production
"""" 
@app.route("/dashboard", methods=['GET', 'POST']) 
@login_required
def dashboard_view():
    if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(Staff.Ruolo == 'Gestore')).count():
        if request.method == 'POST':
            insert_corso(nome=request.form['nome'], min_persone=request.form['minPersone'], max_persone=request.form['maxPersone'], ora_inizio=request.form['oraInizio'], ora_fine=request.form['oraFine'], id_sala=request.form['sala'], id_istruttore=request.form['istruttore'], data=request.form['dataInizio'])

        return render_template('adminDashboard.html', sale=get_sale())
    else:
        abort(401)
"""


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard_view():
    if request.method == 'POST' and 'nome' in request.form:
        start = datetime.strptime(request.form['settimanaInizio'] + '-1', "%Y-W%W-%w")
        reps = int(request.form['ripetizioni'])
        giorni_settimana = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']
        weekdays = [i in request.form.keys() for i in giorni_settimana]
        for i in range(reps):
            for j, v in enumerate(weekdays):
                if v:
                    new_date = start + timedelta(days=j)
                    print(new_date)
            start += timedelta(days=7)
        # insert_corso(nome=request.form['nome'], min_persone=request.form['minPersone'], max_persone=request.form['maxPersone'], ora_inizio=request.form['oraInizio'], ora_fine=request.form['oraFine'], id_sala=request.form['sala'].split(',')[0], id_istruttore=request.form['istruttore'], data=request.form['dataInizio'], descrizione=request.form['descrizione'])

    # TODO: gestire messaggi
    if request.method == 'POST' and 'attivazione' in request.form:
        if 'attivazione' in request.form and request.form['attivazione'] == 'attiva':
            attiva_persona(persona=request.form['codiceFiscale'])
        elif 'attivazione' in request.form and request.form['attivazione'] == 'disattiva':
            disattiva_persona(persona=request.form['codiceFiscale'])

    if request.method == 'POST' and 'pagante' in request.form:
        if 'pagante' in request.form and request.form['pagante'] == 'pagante':
            setta_pagante(cliente=request.form['codiceFiscale'])
        elif 'pagante' in request.form and request.form['pagante'] == 'non pagante':
            setta_non_pagante(cliente=request.form['codiceFiscale'])

    if request.method == 'POST' and 'tipo' in request.form:
        insert_sala(max_persone=request.form['MaxPersone'], tipo=request.form['tipo'])
    if request.method == 'POST' and 'da tracciare' in request.form:
        return redirect(url_for('report', zero=request.form['da tracciare'], giorni=request.form['giorni']))

    return render_template('adminDashboard.html', sale=get_sale())


@app.route("/report/<zero>/<giorni>")
def report(zero, giorni):
    tracciati = contact_tracing(zero=get_persona_by_cf(zero), days=giorni)
    return render_template('report.html', positivi=tracciati)
