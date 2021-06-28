import re
import time
import bcrypt
import pdfkit
from flask import *
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from run import app, db, mail
from appF.models import *


@app.route('/')
def home():
    get_time_step()
    is_admin = (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(
        Staff.Ruolo == 'Gestore')).count() > 0
    return render_template("home.html", admin=is_admin)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and request.form['form-name'] == 'login':
        username = request.form['username']
        password = bytes(request.form['password'],
                         encoding="utf-8")  # todo: controllare se è possibile .encode() chiedere a Mario
        logging = db.session.query(Persona).filter(Persona.Email == username).first()
        if logging is not None and bcrypt.checkpw(password, logging.Password.encode("utf-8")):
            user = get_persona_by_email(request.form['username'])
            login_user(user)
            if (
                    db.session.query(Staff).filter(Staff.IDStaff == user.get_id()).filter(
                        Staff.Ruolo == 'Gestore')).count():
                return redirect(url_for('dashboard_view'))
            else:
                return redirect(url_for('profile_view', username=user.Email))
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
        return redirect(url_for('profile_view', username=current_user.get_email))
    else:
        msg = ''
        if request.method == 'POST' and request.form['form-name'] == 'register':
            email = request.form['email']
            registration = db.session.query(Persona).filter(Persona.Email == email).first()
            cf = db.session.query(Persona).filter(Persona.CF == request.form['Codice fiscale']).first()
            if registration is not None or cf is not None:
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
                                               data_nascita=request.form['DataNascita'],
                                               cf=request.form['Codice fiscale'],
                                               email=request.form['email'], telefono=request.form['telefono'],
                                               sesso=request.form['sex'],
                                               password=bcrypt.hashpw(request.form['password'].encode("utf-8"),
                                                                      bcrypt.gensalt()).decode("utf-8"), attivo=False)
                if (db.session.query(Staff).filter(Staff.IDStaff == current_user.get_id()).filter(
                        Staff.Ruolo == 'Gestore')).count():
                    insert_istruttore(nuova_persona)
                else:
                    insert_cliente(nuova_persona)
                # msg = 'Ti sei registrato con successo!' non visualizzato a causa del redirect
                login_user(nuova_persona)
                return redirect(url_for('profile_view', username=nuova_persona.Email))
        elif request.method == 'POST':
            msg = 'Riempi tutti i campi del form'
        return render_template('register.html', msg=msg)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def profile_view(username):
    msg = ""
    inbox_number = len(db.session.query(NotificaDestinatario)
                       .filter(NotificaDestinatario.Destinatario == current_user.CF,
                               NotificaDestinatario.Letto == False).all())
    if not username == current_user.get_email:
        return redirect(url_for('profile_view', username=current_user.get_email, msg=msg))

    if request.method == 'POST' and request.form['form-name'] == 'prenotazione':
        is_active = db.session.query(Persona.Attivo).filter(Persona.Email == current_user.get_email).first()
        new_book = insert_prenotazione(persona=get_persona_by_email(username), data=request.form['Data'],
                                       ora_inizio=request.form['oraInizio'], ora_fine=request.form['oraFine'],
                                       sala=request.form['IDSala'], corso=request.form['IDCorso'])

        if new_book is None:
            msg = 'Errore fatale, la data scelta non è valida'
        elif not is_active:
            # todo: messaggio provvisorio
            msg = 'Non sei ancora autorizzato ad accedere alla palestra,' \
                  'la tua prenotazione è registrata ma è in attesa di validazione, ' \
                  'contatta il gestore per essere abilitato'
        elif not new_book.Approvata:
            msg = 'Tutto pieno, sei stato messo in coda'
        else:
            msg = 'Prenotazione effettuata con successo'

    return render_template('user_page.html', persona=get_persona_by_email(username), username=username, msg=msg,
                           inbox_number=inbox_number)


@app.route('/calendar')
def calendar_view_today():
    user = request.args.get('user')
    return redirect(url_for('calendar_view', anno=datetime.today().year, mese=datetime.today().month, user=user))


@app.route('/calendar/<int:anno>/<int:mese>', methods=['GET', 'POST'])
def calendar_view(anno, mese):
    user = request.args.get('user')
    if user is None:
        corsi = get_corsi(mese, anno)
        for c in corsi: print(c)
    else:
        print(user.Email)
        corsi = get_prenotazioni_persona(user, mese, anno)
        corsi += (get_corsi_seguiti(user))
    return render_template('calendar.html', corsi=corsi, anno=anno, mese=mese)


@app.route("/corsi")
def lista_corsi():
    corsi = get_corsi_futuri()
    return render_template('corsi.html', lista_corsi=corsi)


@app.route("/corso/<id>", methods=['GET', 'POST'])
def view_corso(id):
    corso = db.session.query(Corso).filter(Corso.IDCorso == id).first()
    istruttore = db.session.query(Persona).filter(Persona.CF == corso.IDIstruttore).first()

    if request.method == 'POST' and current_user.is_authenticated:
        if request.form['form-name'] == "iscriviti":
            insert_prenotazione(current_user, corso.Data, corso.OraInizio, corso.OraFine, corso.IDSala, corso.IDCorso)
            # TODO: gestire eventuali messaggi per mancata disponibilità ecc..
        elif request.form['form-name'] == "follow":
            insert_corso_seguito(persona=current_user.get_id(), corso=corso.Nome)
            print(str(current_user.get_id()) + "vuole iscriversi")
        # TODO: unfollow?

    return render_template('corso.html', corso=corso, istruttore=istruttore,
                           iscritti=numero_iscritti_corso(corso.IDCorso),
                           seguito=is_seguito(current_user.get_id(), corso.Nome))


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
    if request.method == 'POST' and request.form['form-name'] == 'inserisciCorso':
        start = datetime.strptime(request.form['settimanaInizio'] + '-1', "%Y-W%W-%w")
        reps = int(request.form['ripetizioni'])
        giorni_settimana = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']
        weekdays = [i in request.form.keys() for i in giorni_settimana]
        for _ in range(reps):
            for j, v in enumerate(weekdays):
                if v:
                    new_date = start + timedelta(days=j)
                    insert_corso(nome=request.form['nome'], min_persone=request.form['minPersone'],
                                 max_persone=request.form['maxPersone'], ora_inizio=request.form['oraInizio'],
                                 ora_fine=request.form['oraFine'], id_sala=request.form['sala'].split(',')[0],
                                 id_istruttore=request.form['istruttore'], data=new_date,
                                 descrizione=request.form['descrizione'])
            start += timedelta(days=7)

    # TODO: gestire messaggi
    if request.method == 'POST' and request.form['form-name'] == 'opzioniPersona':
        if 'attivazione' in request.form and request.form['attivazione'] == 'attiva':
            attiva_persona(persona=request.form['codiceFiscale'])
        elif 'attivazione' in request.form and request.form['attivazione'] == 'disattiva':
            disattiva_persona(persona=request.form['codiceFiscale'])

    if request.method == 'POST' and request.form['form-name'] == 'opzioniClienti':
        if 'pagante' in request.form and request.form['pagante'] == 'pagante':
            setta_pagante(cliente=request.form['codiceFiscale'])
        elif 'pagante' in request.form and request.form['pagante'] == 'non pagante':
            setta_non_pagante(cliente=request.form['codiceFiscale'])

    if request.method == 'POST' and request.form['form-name'] == 'creaSala':
        insert_sala(max_persone=request.form['MaxPersone'], tipo=request.form['tipo'])
    if request.method == 'POST' and request.form['form-name'] == 'tracciamento':
        return redirect(url_for('report', zero=request.form['da tracciare'], giorni=request.form['giorni']))

    return render_template('adminDashboard.html', sale=get_sale(), istruttori=get_istruttori())


@app.route("/report/<zero>/<giorni>", methods=['GET', 'POST'])
def report(zero, giorni):
    messaggio = ""
    tracciati = contact_tracing(zero=get_persona_by_cf(zero), days=giorni)
    if request.method == 'POST':
        form = request.form['form-name']
        if form == 'esporta':
            # path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # path di mario, da modificare
            # pdf_config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
            rendered = render_template('printable_report.html', zero=get_persona_by_cf(zero), positivi=tracciati,
                                       giorni=giorni)
            pdf = pdfkit.from_string(rendered, False)  # , configuration=pdf_config)
            response = make_response(pdf)
            response.headers['Content-Type'] = 'report'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        if form == 'notifica' or form == 'disattiva':
            # TODO: email non funzionante, da configurare
            """
            subject = "Segnalazione possibile contagio"
            sender = (db.session.query(Persona).filter(Persona.CF == 'ADMINADMIN').first()).Email
            # msg.html = render_template('', ...)
            for person in tracciati:
                msg = Message(subject=subject, sender=sender, recipients=person.Email)
                if form == 'disattiva':
                    msg.body = "potresti essere stato contagiato e sei disattivato, caro" + person.Nome
                    disattiva_persona(persona=person.CF)
                else:
                    msg.body = "potresti essere stato contagiato, caro" + person.Nome
                mail.send(msg)
            messaggio = "operazione avvenuta con successo"
            """
            for person in tracciati:
                if form == 'disattiva':
                    notifica = db.session.query(Notifica).filter(
                        Notifica.IDNotifica == 0).first()  # da creare con un codice particolare
                    disattiva_persona(persona=person.CF)
                else:
                    notifica = db.session.query(Notifica).filter(
                        Notifica.IDNotifica == 1).first()  # da creare con un codice particolare
                invia_notifica(notifica=notifica, destinatari=[person.CF])
    return render_template('report.html', msg=messaggio, zero=zero, giorni=giorni, positivi=tracciati)


@app.route("/notifiche", methods=['GET', 'POST'])
@login_required
def notifications():
    sender = False
    if current_user.CF in [member.IDStaff for member in db.session.query(Staff).all()]:
        sender = True
    notify_ids = [i.IDNotifica for i in db.session.query(NotificaDestinatario).filter(
        NotificaDestinatario.Destinatario == current_user.CF).all()]
    notifies = db.session.query(Notifica).filter(Notifica.IDNotifica.in_(notify_ids)).all()
    inbox = []
    for notify in notifies:
        message = {'IDNotifica': notify.IDNotifica,
                   'Mittente': get_persona_by_cf(notify.Mittente).Email,
                   'Timestamp': db.session.query(NotificaDestinatario).filter(
                       NotificaDestinatario.IDNotifica == notify.IDNotifica,
                       NotificaDestinatario.Destinatario == current_user.CF).first().Timestamp,
                   'Letto': db.session.query(NotificaDestinatario).filter(
                       NotificaDestinatario.IDNotifica == notify.IDNotifica,
                       NotificaDestinatario.Destinatario == current_user.CF).first().Letto,
                   'Testo': notify.Testo}
        inbox.append(message)
    if sender and request.method == 'POST' and request.form['form-name'] == 'inviaNotifica':
        testo = request.form['testo']
        mittente = current_user.CF
        destinatari = request.form['destinatario'].split(' ')
        notifica = crea_notifica(testo=testo, mittente=mittente)
        invia_notifica(notifica=notifica, destinatari=destinatari)
    db.session.query(NotificaDestinatario) \
        .filter(NotificaDestinatario.Destinatario == current_user.CF).update({'Letto': True})
    db.session.commit()
    return render_template('notifiche.html', sender=sender, inbox=inbox)
