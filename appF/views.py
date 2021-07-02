import re
import bcrypt
import pdfkit
from functools import wraps
from flask import *
from flask_login import login_user, logout_user, login_required, current_user

from run import app
from appF.models import *


def auth_admin(f):  # decoratore per le view che richiedono autorizzazione di amministratore
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and request.form['form-name'] == 'login':
        username = request.form['username']
        password = bytes(request.form['password'],
                         encoding="utf-8")
        logging = get_persona_by_email(username)
        if logging is not None and bcrypt.checkpw(password, logging.Password.encode("utf-8")):
            user = get_persona_by_email(request.form['username'])
            login_user(user)
            if current_user.is_admin():
                return redirect(url_for('dashboard_view'))
            else:
                return redirect(url_for('profile_view'))
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
    if current_user.is_authenticated and not current_user.is_admin():
        return redirect(url_for('profile_view'))
    else:
        msg = ''
        if request.method == 'POST' and request.form['form-name'] == 'register':
            email = request.form['email']
            registration = get_persona_by_email(email)
            cf = get_persona_by_cf(request.form['Codice fiscale'])
            if registration is not None or cf is not None:
                msg = 'Persona già registrata'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Indirizzo email non valido'
            elif len(request.form['Codice fiscale']) != 16:
                msg = 'Codice fiscale non valido'
            else:
                nuova_persona = insert_persona(nome=request.form['name'], cognome=request.form['surname'],
                                               data_nascita=request.form['DataNascita'],
                                               cf=request.form['Codice fiscale'],
                                               email=request.form['email'], telefono=request.form['telefono'],
                                               sesso=request.form['sex'],
                                               password=bcrypt.hashpw(request.form['password'].encode("utf-8"),
                                                                      bcrypt.gensalt()).decode("utf-8"), attivo=False)
                if current_user.is_authenticated and current_user.is_admin():
                    insert_istruttore(nuova_persona)
                    return redirect(url_for('dashboard_view'))
                else:
                    insert_cliente(nuova_persona)
                    login_user(nuova_persona)
                invia_notifica(session_utente.query(Notifica).filter(Notifica.IDNotifica == 3).first(),
                               [nuova_persona.CF])
                return redirect(url_for('profile_view'))
        elif request.method == 'POST':
            msg = 'Riempi tutti i campi del form'
        return render_template('register.html', msg=msg)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def profile_view():
    if request.method == 'POST' and request.form['form-name'] == 'prenotazione':
        if datetime.strptime(request.form['Data'], "%Y-%m-%d") <= datetime.today() + timedelta(days=14):
            insert_prenotazione(persona=get_persona_by_email(current_user.get_email), data=request.form['Data'],
                                ora_inizio=(request.form['oraOraInizio'] + ":" + request.form['minutiOraInizio']),
                                ora_fine=(request.form['oraOraFine'] + ":" + request.form['minutiOraFine']),
                                sala=request.form['sala'])

    if current_user.is_admin():
        return redirect(url_for("dashboard_view"))

    inbox_number = len(session_utente.query(NotificaDestinatario)
                       .filter(NotificaDestinatario.Destinatario == current_user.CF,
                               NotificaDestinatario.Letto == False).all())

    return render_template('user_page.html', persona=current_user.get_id(),
                           inbox_number=inbox_number, step=get_time_step(), sale=get_sale(),
                           prenotazioni=get_all_prenotazioni_persona(current_user.get_id()))


@app.route('/calendar')
@login_required
def calendar_view_today():
    return redirect(url_for('calendar_view', anno=datetime.today().year, mese=datetime.today().month))


@app.route('/calendar/<int:anno>/<int:mese>', methods=['GET', 'POST'])
@login_required
def calendar_view(anno, mese):
    if current_user.is_admin():
        corsi = get_corsi(mese, anno)
    elif current_user.is_staff():
        corsi = get_corsi_insegnante(current_user.get_id(), mese, anno)
    else:
        corsi = get_prenotazioni_persona(current_user.get_id(), mese, anno)
        corsi += (get_corsi_seguiti(current_user.get_id()))
    return render_template('calendar.html', corsi=corsi, anno=anno, mese=mese)


@app.route("/corsi")
def lista_corsi():
    corsi = get_corsi_futuri()
    return render_template('corsi.html', lista_corsi=corsi)


@app.route("/corso/<id>", methods=['GET', 'POST'])
def view_corso(id):
    corso = get_corso_by_id(id)

    if corso is None:
        abort(404)
    istruttore = get_persona_by_cf(corso.IDIstruttore)

    if request.method == 'POST' and current_user.is_authenticated:
        if request.form['form-name'] == "subscribe":
            insert_prenotazione(current_user, corso.Data, corso.OraInizio, corso.OraFine, corso.IDSala, corso.IDCorso)
        elif request.form['form-name'] == "follow":
            insert_corso_seguito(persona=current_user.get_id(), corso=corso.Nome)
        elif request.form['form-name'] == "unfollow":
            delete_corso_seguito(persona=current_user.get_id(), corso=corso.Nome)
        elif request.form['form-name'] == "unsubscribe":
            delete_prenotazione_corso(persona=current_user.get_id(), corso=corso.IDCorso)
        elif request.form['form-name'] == "delete":
            delete_corso(corso=corso.IDCorso)
            return redirect(url_for("dashboard_view"))
        elif request.form['form-name'] == 'inviaNotifica':
            nuova_notifica = crea_notifica(request.form['testo'], current_user.CF)
            destinatari = [p.IDCliente for p in get_iscritti_corso(corso.IDCorso)] + \
                          [p.IDCliente for p in get_follower_corso(corso.IDCorso)]
            destinatari = list(set(destinatari))
            invia_notifica(nuova_notifica, destinatari)

    return render_template('corso.html', corso=corso, istruttore=istruttore,
                           iscritti=numero_iscritti_corso(corso.IDCorso),
                           is_seguito=is_seguito(current_user.get_id(), corso.Nome),
                           is_iscritto=is_iscritto(current_user.get_id(), corso.IDCorso))


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
@auth_admin
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
                                 max_persone=request.form['maxPersone'],
                                 ora_inizio=(request.form['oraOraInizio'] + ":" + request.form['minutiOraInizio']),
                                 ora_fine=(request.form['oraOraFine'] + ":" + request.form['minutiOraFine']),
                                 id_sala=request.form['sala'].split(',')[0],
                                 id_istruttore=request.form['istruttore'], data=new_date,
                                 descrizione=request.form['descrizione'])
            start += timedelta(days=7)
    if request.method == 'POST' and request.form['form-name'] == 'creaSala':
        insert_sala(max_persone=request.form['MaxPersone'], tipo=request.form['tipo'])
    if request.method == 'POST' and request.form['form-name'] == "modificaScaglione":
        session_gestore.query(Generali).update({'MinutiScaglioni': request.form['slot']})
        session_gestore.commit()
    if request.method == 'POST' and request.form['form-name'] == 'limiti':
        if request.form['maxOre'] != '':
            session_gestore.query(Generali).update({'MassimoOreGiorno': request.form['maxOre']})
        if request.form['maxGiorni'] != '':
            session_gestore.query(Generali).update({'MassimoGiorniSettimana': request.form['maxGiorni']})
        session_gestore.commit()
    if request.method == 'POST' and request.form['form-name'] == 'tracciamento':
        session_gestore.query(Generali).update({'GiorniTracciamento': request.form['giorni']})
        session_gestore.commit()

    return render_template('adminDashboard.html', sale=get_sale(), istruttori=get_istruttori(), step=get_time_step())


@app.route("/report", methods=['GET', 'POST'])
def report():
    messaggio = ""
    zero = request.args.get('zero')
    giorni = request.args.get('giorni')
    tracciati = contact_tracing(zero=get_persona_by_cf(zero), days=giorni)

    if request.method == 'POST':
        form = request.form['form-name']
        if form == 'esporta':
            rendered = render_template('printable_report.html', zero=get_persona_by_cf(zero), positivi=tracciati,
                                       giorni=giorni)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['Content-Type'] = 'report'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        if form == 'notifica' or form == 'disattiva':
            for person in tracciati:
                if form == 'disattiva':
                    notifica = session_utente.query(Notifica).filter(
                        Notifica.IDNotifica == 0).first()
                    disattiva_persona(persona=person.CF)
                else:
                    notifica = session_utente.query(Notifica).filter(
                        Notifica.IDNotifica == 1).first()
                invia_notifica(notifica=notifica, destinatari=[person.CF])
            messaggio = 'operazione avvenuta con successo'

    return render_template('report.html', msg=messaggio, zero=zero, giorni=giorni, positivi=tracciati)


@app.route("/notifiche", methods=['GET', 'POST'])
@login_required
def notifications():
    if request.method == 'POST' and request.form['form-name'] == 'cancellaNotifiche':
        q = delete(NotificaDestinatario).where(NotificaDestinatario.Destinatario == current_user.CF)
        session_utente.execute(q)
        session_utente.commit()
    if current_user.is_staff() and request.method == 'POST' and request.form['form-name'] == 'inviaNotifica':
        testo = request.form['testo']
        mittente = current_user.CF
        destinatari = request.form['destinatario'].split(' ')
        notifica = crea_notifica(testo=testo, mittente=mittente)
        invia_notifica(notifica=notifica, destinatari=destinatari)

    inbox = get_notifiche_persona(current_user.get_id())

    session_utente.query(NotificaDestinatario).filter(NotificaDestinatario.Destinatario == current_user.CF) \
        .update({'Letto': True})
    session_utente.commit()

    return render_template('notifiche.html', inbox=inbox)


@app.route("/prenotazione/<id_prenotazione>", methods=['GET', 'POST'])
@login_required
def prenotazione_view(id_prenotazione):
    if request.method == 'POST' and request.form['form-name'] == 'delete':
        delete_prenotazione_by_id(id_prenotazione)
        return redirect(url_for('profile_view'))

    p = get_prenotazione_by_id(id_prenotazione)
    if p is None:
        return abort(404)
    if current_user.get_id() != p['IDCliente']:
        return abort(403)

    stringa_qr = 'IDPrenotazione: ' + str(p['IDPrenotazione']) + \
                 '\nData: ' + str(p['Data']) + '\nOra inizio: ' + str(p['OraInizio']) + \
                 '\nOra fine: ' + str(p['OraFine']) + '\nSala: ' + str(p['IDSala'])

    c = None
    if p['IDCorso']:
        c = get_corso_by_id(p['IDCorso'])

    return render_template('prenotazione.html', prenotazione=p, corso=c, stringaQR=stringa_qr)


@app.route("/users", methods=['GET', 'POST'])
@login_required
@auth_admin
def view_users():
    clienti = session_ospite.query(Persona).filter(Persona.CF.in_(session_ospite.query(Cliente.IDCliente))).order_by(
        Persona.Cognome, Persona.Nome).all()
    staff = session_ospite.query(Persona).filter(Persona.CF.in_(session_ospite.query(Staff.IDStaff))).order_by(
        Persona.Cognome, Persona.Nome).all()

    for i, v in enumerate(clienti):
        c = {
            'Nome': v.Nome,
            'Cognome': v.Cognome,
            'CF': v.CF,
            'Email': v.Email,
            'Attivo': v.Attivo,
            'Pagante': get_cliente_by_id(v.CF).PagamentoMese
        }
        clienti[i] = c
    for i, v in enumerate(staff):
        s = {
            'Nome': v.Nome,
            'Cognome': v.Cognome,
            'CF': v.CF,
            'Email': v.Email,
            'Ruolo': session_ospite.query(Staff).filter(Staff.IDStaff == v.CF).first().Ruolo,
            'Attivo': v.Attivo
        }
        staff[i] = s

    if request.method == 'POST' and request.form['form-name'] == 'modifica':
        for p in clienti:
            if 'attivazione-' + p['CF'] in request.form:
                attiva_persona(p['CF'])
                p['Attivo'] = True
            else:
                disattiva_persona(p['CF'])
                p['Attivo'] = False

            if 'pagamento-' + p['CF'] in request.form:
                setta_pagante(p['CF'])
                p['Pagante'] = True
            else:
                setta_non_pagante(p['CF'])
                p['Pagante'] = False

        for p in staff:
            if 'attivazione-' + p['CF'] in request.form:
                attiva_persona(p['CF'])
                p['Attivo'] = True
            else:
                disattiva_persona(p['CF'])
                p['Attivo'] = False

    return render_template('users.html', clienti=clienti, staff=staff, giorni_tracciamento=get_giorni_tracciamento())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401
