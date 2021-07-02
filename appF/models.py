import datetime

from config import SQLALCHEMY_DATABASE_URI_UTENTE
from run import engine_ospite, engine_utente, engine_istruttore, engine_gestore  # , engine
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import *
from flask_login import UserMixin
from sqlalchemy import create_engine

Base = declarative_base()  # tabella = classe che eredita da Base


class Sala(Base):
    __tablename__ = 'sale'

    IDSala = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    Tipo = Column(TEXT)

    def __repr__(self):
        return "<Sala: ID='%s', MaxP='%s', Tipo='%s'>" % (self.IDSala, self.MaxPersone, self.Tipo)


class Persona(UserMixin, Base):
    __tablename__ = 'persone'

    CF = Column(CHAR(16), primary_key=True)
    Nome = Column(VARCHAR, nullable=False)
    Cognome = Column(VARCHAR, nullable=False)
    Sesso = Column('Sesso', Enum('M', 'F'), nullable=False)
    DataNascita = Column(DATE, nullable=False)
    Email = Column(TEXT, nullable=False, unique=True)
    Password = Column(TEXT, nullable=False)
    Telefono = Column(TEXT)
    Attivo = Column(BOOLEAN, nullable=False)

    def is_active(self):
        return self.Attivo

    def is_staff(self):
        return session_ospite.query(Staff).filter(Staff.IDStaff == self.CF).first() is not None

    def can_book(self):
        return not self.is_staff() and self.Attivo and get_cliente_by_id(self.CF).PagamentoMese

    def get_id(self):
        return self.CF

    @property
    def get_email(self):
        return str(self.Email)

    def is_admin(self):
        return (session_ospite.query(Staff).filter(Staff.IDStaff == self.CF).filter(
            Staff.Ruolo == 'Gestore')).count() > 0

    def __repr__(self):
        return "<Persona: CF='%s', N='%s', C='%s', S='%s', DN='%s', Email='%s', PW='%s', Tel='%s', Act='%s'>" % (
            self.CF, self.Nome, self.Cognome, self.Sesso, self.DataNascita, self.Email, self.Password, self.Telefono,
            self.Attivo)


class OrarioPalestra(Base):
    __tablename__ = 'orariPalestra'

    Apertura = Column(DATE, primary_key=True)
    Chiusura = Column(DATE, primary_key=True)
    GiornoSettimana = Column(INTEGER, primary_key=True)

    def __repr__(self):
        return "<Palestra: A='%s', C='%s', Day='%s>" % (self.Apertura, self.Chiusura, self.GiornoSettimana)


class GiornoFestivo(Base):
    __tablename__ = 'giorniFestivi'

    Apertura = Column(TIME)
    Chiusura = Column(TIME)
    Giorno = Column(DATE, primary_key=True)


class Generali(Base):
    __tablename__ = 'generali'

    MinutiScaglioni = Column(INTEGER, primary_key=True)
    MassimoGiorniSettimana = Column(INTEGER)
    MassimoOreGiorno = Column(INTEGER)
    GiorniTracciamento = Column(INTEGER)


class Notifica(Base):
    __tablename__ = 'notifiche'

    IDNotifica = Column(INTEGER, primary_key=True)
    Testo = Column(TEXT, nullable=False)
    Mittente = Column(CHAR(16), ForeignKey(Persona.CF))

    mittenti = relationship(Persona, uselist=False)

    def __repr__(self):
        return "<Notifica: ID:'%s', Mittente:'%s', Testo:'%s'>" % (self.IDNotifica, self.Mittente, self.Testo)


class Cliente(Base):
    __tablename__ = 'clienti'

    IDCliente = Column(CHAR(16), ForeignKey(Persona.CF), primary_key=True)
    DataIscrizione = Column(DATE, nullable=False)
    PagamentoMese = Column(BOOLEAN, nullable=False)

    persone = relationship(Persona, uselist=False)

    def __repr__(self):
        return "<Clienti: ID:'%s', DatIscr:'%s', PagMese:'%s'>" % (
            self.IDCliente, self.DataIscrizione, self.PagamentoMese)


class Staff(Base):
    __tablename__ = 'staff'

    IDStaff = Column(CHAR(16), ForeignKey(Persona.CF), primary_key=True)
    Ruolo = Column('Ruolo', Enum('Istruttore', 'Gestore'), nullable=False)

    persone = relationship(Persona, uselist=False)

    def __repr__(self):
        return "<Staff: ID:'%s', Role:'%s'>" % (self.IDStaff, self.Ruolo)


class Corso(Base):
    __tablename__ = 'corsi'

    IDCorso = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    MinPersone = Column(SMALLINT, nullable=False)
    IDSala = Column(INTEGER, ForeignKey(Sala.IDSala), nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    Data = Column(DATE, nullable=False)
    Descrizione = Column(TEXT)
    Nome = Column(VARCHAR, nullable=False)
    IDIstruttore = Column(CHAR(16), ForeignKey(Staff.IDStaff), nullable=False)

    sale = relationship(Sala, uselist=False)
    staff = relationship(Staff, uselist=False)

    def __repr__(self):
        return "ID:%s, Nome:%s, Max:%s, Min:%s, IDSala:%s, OInizio:%s, OFine:%s, Data:%s, Descr:%s, IDIstr:%s" % (
            self.IDCorso, self.Nome, self.MaxPersone, self.MinPersone, self.IDSala, self.OraInizio, self.OraFine,
            self.Data,
            str(self.Descrizione), self.IDIstruttore)


class Prenotazione(Base):
    __tablename__ = 'prenotazioni'

    IDPrenotazione = Column(INTEGER, primary_key=True)
    Data = Column(DATE, nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    IDCliente = Column(VARCHAR, ForeignKey(Cliente.IDCliente), nullable=False)
    IDCorso = Column(INTEGER, ForeignKey(Corso.IDCorso))
    IDSala = Column(INTEGER, ForeignKey(Sala.IDSala), nullable=False)
    Approvata = Column(BOOLEAN, nullable=False, default=True)

    clienti = relationship(Cliente, uselist=False)
    corsi = relationship(Corso, uselist=False)
    sale = relationship(Sala, uselist=False)

    def __repr__(self):
        return "<Prenotazioni: ID:'%s', Data:'%s', OInizio:'%s', OFine:'%s', IDCliente:'%s', IDCorso:'%s', IDSala:'%s', Aprr:'%s'>" % \
               (self.IDPrenotazione, self.Data, self.OraInizio, self.OraFine, self.IDCliente, self.IDCorso, self.IDSala,
                self.Approvata)


class NotificaDestinatario(Base):
    __tablename__ = 'notificaDestinatario'

    IDNotifica = Column(INTEGER, ForeignKey(Notifica.IDNotifica), primary_key=True)
    Destinatario = Column(CHAR(16), ForeignKey(Persona.CF), primary_key=True)
    Timestamp = Column(TIMESTAMP, primary_key=True)
    Letto = Column(BOOLEAN, nullable=False)

    notifiche = relationship(Notifica, uselist=False)
    destinatari = relationship(Persona, uselist=False)

    def __repr__(self):
        return "<NotificaD: ID:'%s', Destinatario:'%s', timestamp:'%s', letto:'%s'>" % (
            self.IDNotifica, self.Destinatario, self.Timestamp, self.Letto)


class CorsoSeguito(Base):
    __tablename__ = 'corsiSeguiti'

    IDCliente = Column(CHAR(16), ForeignKey(Cliente.IDCliente), primary_key=True)
    Nome = Column(TEXT, primary_key=True)

    clienti = relationship(Cliente, uselist=False)


# Session = sessionmaker(bind=engine)
# session = Session()
Session_ospite = sessionmaker(bind=engine_ospite)  # creazione delle factory
session_ospite = Session_ospite()
Session_utente = sessionmaker(bind=engine_utente)
session_utente = Session_utente()
Session_istruttore = sessionmaker(bind=engine_istruttore)
session_istruttore = Session_istruttore()
Session_gestore = sessionmaker(bind=engine_gestore)
session_gestore = Session_gestore()


def insert_persona(cf, nome, cognome, sesso, data_nascita, email, password, attivo, telefono=None):
    to_add = Persona(CF=cf, Nome=nome, Cognome=cognome, Sesso=sesso, DataNascita=data_nascita, Email=email,
                     Password=password, Attivo=attivo, Telefono=telefono)
    session_ospite.add(to_add)
    session_ospite.commit()
    return to_add


def insert_cliente(persona):
    to_add = Cliente(IDCliente=persona.CF, DataIscrizione=date.today(), PagamentoMese=False)
    session_ospite.add(to_add)
    session_ospite.commit()


def get_cliente_by_id(cliente):
    return session_ospite.query(Cliente).filter(Cliente.IDCliente == cliente).first()


def insert_istruttore(persona):
    to_add = Staff(IDStaff=persona.CF, Ruolo='Istruttore')
    session_gestore.add(to_add)
    session_gestore.commit()


def insert_corso(max_persone, min_persone, id_sala, ora_inizio, ora_fine, data, id_istruttore, nome, descrizione=None):
    c = Corso(MaxPersone=max_persone, MinPersone=min_persone, IDSala=id_sala, OraInizio=ora_inizio, OraFine=ora_fine,
              Data=data, IDIstruttore=id_istruttore, Descrizione=descrizione, Nome=nome)
    session_istruttore.add(c)
    session_istruttore.commit()


def delete_corso(corso):
    q = delete(Corso).where(Corso.IDCorso == corso)
    session_istruttore.execute(q)
    session_istruttore.commit()


def get_corsi(mese, anno):
    q = session_ospite.query(Corso).filter(extract('year', Corso.Data) == anno).filter(
        extract('month', Corso.Data) == mese).order_by(Corso.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "corso"
        del ret[-1]['_sa_instance_state']
    return ret


def get_corsi_futuri():
    q = session_ospite.query(Corso).filter(Corso.Data >= date.today(), Corso.OraInizio > time()).order_by(
        Corso.Data).all()
    return q


def get_corso_by_id(id):
    q = session_ospite.query(Corso).filter(Corso.IDCorso == id).first()
    return q


def numero_iscritti_corso(corso):
    iscr = session_ospite.query(Prenotazione).filter(Prenotazione.IDCorso == corso).filter(
        Prenotazione.Approvata).count()
    return iscr


def get_iscritti_corso(corso):
    iscr = session_ospite.query(Prenotazione).filter(Prenotazione.IDCorso == corso).filter(Prenotazione.Approvata).all()
    return iscr


def get_follower_corso(corso):
    flw = session_utente.query(CorsoSeguito).filter(CorsoSeguito.Nome == get_corso_by_id(corso).Nome).all()
    return flw


def get_sale():
    q = session_utente.query(Sala).all()
    return q


def get_istruttori():
    q = session_ospite.query(Staff.IDStaff, Persona.Nome, Persona.Cognome).filter(Staff.Ruolo == "Istruttore",
                                                                                  Persona.CF == Staff.IDStaff).all()
    return q


def get_persona_by_email(email):
    q = session_ospite.query(Persona).filter(Persona.Email == email)
    return q.one()


def get_persona_by_cf(cf):
    q = session_ospite.query(Persona).filter(Persona.CF == cf)
    return q.first()


def attiva_persona(cf):
    session_gestore.query(Persona).filter(Persona.CF == cf).update({'Attivo': True})
    session_gestore.commit()


def disattiva_persona(persona):
    session_gestore.query(Persona).filter(Persona.CF == persona).update({'Attivo': False})
    session_gestore.query(Prenotazione).filter(Prenotazione.IDCliente == persona,
                                               Prenotazione.Data >= datetime.today()  # ,
                                               # Prenotazione.OraInizio >= datetime.now())\
                                               ).update({'Approvata': False})
    session_gestore.commit()


def setta_pagante(cliente):
    session_gestore.query(Cliente).filter(Cliente.IDCliente == cliente).update({'PagamentoMese': True})
    session_gestore.commit()


def setta_non_pagante(cliente):
    session_gestore.query(Cliente).filter(Cliente.IDCliente == cliente).update({'PagamentoMese': False})
    session_gestore.commit()


def insert_sala(max_persone, tipo):
    to_add = Sala(MaxPersone=max_persone, Tipo=tipo)
    session_gestore.add(to_add)
    session_gestore.commit()


def get_time_step():
    q = session_utente.query(Generali).one().MinutiScaglioni
    return q


def get_prenotazione_by_id(id):
    q = session_ospite.query(Prenotazione).filter(Prenotazione.IDPrenotazione == id).first()
    if q is None:
        return None
    return q.__dict__


def insert_prenotazione(persona, data, ora_inizio, ora_fine, sala, corso=None):
    secure_engine = create_engine(SQLALCHEMY_DATABASE_URI_UTENTE, isolation_level='SERIALIZABLE')
    Secure_session = sessionmaker(bind=secure_engine)
    secure_session = Secure_session()
    secure_session.begin()
    approved = True
    day = (int(datetime.date(datetime.strptime(str(data), '%Y-%m-%d')).weekday()) + 1 ) % 7 +1
    time_step = get_time_step()
    if int(str(ora_inizio).split(':')[1]) % time_step != 0 or int(str(ora_fine).split(':')[1]) % time_step != 0:
        return None

    orari_giorno = secure_session.query(GiornoFestivo).filter(GiornoFestivo.Giorno == data).first()
    if orari_giorno is None:
        orari_giorno = secure_session.query(OrarioPalestra).filter(OrarioPalestra.GiornoSettimana == day).first()

    if orari_giorno is None or datetime.strptime(str(ora_inizio)[0:5], '%H:%M').time() < orari_giorno.Apertura or \
            datetime.strptime(str(ora_fine)[0:5], '%H:%M').time() > orari_giorno.Chiusura:
        return None

    if corso is None:
        max_number = secure_session.query(Sala).filter(Sala.IDSala == sala).first().MaxPersone
        available = secure_session.query(Prenotazione).filter(Prenotazione.Data == data,
                                                              Prenotazione.OraFine > ora_inizio,
                                                              Prenotazione.OraInizio < ora_fine,
                                                              Prenotazione.IDSala == sala, Prenotazione.Approvata).all()

        inizio_allenamento = int(str(ora_inizio).split(':')[0]) * (60 // time_step) + int(
            str(ora_inizio).split(':')[1]) // time_step
        fine_allenamento = int(str(ora_fine).split(':')[0]) * (60 // time_step) + int(
            str(ora_fine).split(':')[1]) // time_step
        my_time = [0] * (fine_allenamento - inizio_allenamento)

        for booked in available:
            start = (int(str(booked.OraInizio).split(':')[0]) - inizio_allenamento) * (60 // time_step) + int(
                str(booked.OraInizio).split(':')[1]) // time_step
            end = (int(str(booked.OraFine).split(':')[0]) - inizio_allenamento) * (60 // time_step) + int(
                str(booked.OraFine).split(':')[1]) // time_step
            for t in range(max(start, 0), min(end, len(my_time))):
                my_time[t] += 1
        for t in my_time:
            if max_number - t < 1:
                approved = False
                break
        new_book = Prenotazione(Data=data, OraInizio=ora_inizio, OraFine=ora_fine, IDCliente=persona.CF,
                                IDCorso=None, IDSala=sala, Approvata=approved)

    else:
        disponibilita_corso = secure_session.query(Corso).filter(Corso.IDCorso == corso).first().MaxPersone
        if disponibilita_corso - numero_iscritti_corso(corso) < 1:
            approved = False
        new_book = Prenotazione(Data=data, OraInizio=ora_inizio, OraFine=ora_fine, IDCliente=persona.CF,
                                IDCorso=corso, IDSala=sala, Approvata=approved)
    secure_session.add(new_book)
    secure_session.commit()


def delete_prenotazione_corso(persona, corso):
    q = delete(Prenotazione).where(Prenotazione.IDCliente == persona, Prenotazione.IDCorso == corso)
    session_utente.execute(q)
    session_utente.commit()


def delete_prenotazione_by_id(id):
    q = delete(Prenotazione).where(Prenotazione.IDPrenotazione == id)
    session_utente.execute(q)
    session_utente.commit()


def is_iscritto(persona, corso):
    if persona is not None and session_ospite.query(Prenotazione).filter(Prenotazione.IDCliente == persona,
                                                                         Prenotazione.IDCorso == corso).count() > 0:
        return True
    return False


def contact_tracing(zero, days):
    """
    rudimentale algoritmo di contact tracing che prende in input un positivo e un numero di giorni da analizzare
    e ritorna una lista di potenziali positivi
    TODO: testare su corsi e istruttori

    :param zero: positivo iniziale
    :param days: numero di giorni che si vuole prendere in considerazione (max=7)
    :return: lista di potenziali positivi
    """
    potential_infected = [zero.CF]
    days = int(days)
    if days > 7:
        days = 7

    last_zero_appearance_date = session_ospite.query(Prenotazione).filter(
        Prenotazione.IDCliente == zero.CF, Prenotazione.Data <= datetime.today(),
        Prenotazione.Approvata == true()).order_by(Prenotazione.Data.desc()).first()
    if last_zero_appearance_date is not None:
        last_zero_appearance_date = last_zero_appearance_date.Data
    else:
        return [get_persona_by_cf(zero.CF)]
    lower_limit_date = last_zero_appearance_date - timedelta(days=days)
    last_zero_appearances = session_ospite.query(Prenotazione) \
        .filter(Prenotazione.IDCliente == zero.CF, Prenotazione.Data >= lower_limit_date,
                Prenotazione.Data <= datetime.today(),  # da testare
                Prenotazione.Approvata == true()).order_by(Prenotazione.Data.desc()).all()

    for appearance in last_zero_appearances:
        prenotazioni = session_ospite.query(Prenotazione).filter(
            Prenotazione.Data == appearance.Data, Prenotazione.IDSala == appearance.IDSala,
            or_(
                or_(
                    and_(Prenotazione.OraInizio <= appearance.OraInizio, appearance.OraInizio <= Prenotazione.OraFine),
                    and_(Prenotazione.OraInizio <= appearance.OraFine, appearance.OraFine <= Prenotazione.OraFine)),
                or_(
                    and_(appearance.OraInizio <= Prenotazione.OraInizio, Prenotazione.OraInizio <= appearance.OraFine),
                    and_(appearance.OraInizio <= Prenotazione.OraFine, Prenotazione.OraFine <= appearance.OraFine))),
            Prenotazione.Approvata == true()).all()

        if appearance.IDCorso is not None:
            istruttore = session_ospite.query(Corso).filter(Corso.IDCorso == appearance.IDCorso).first().IDIstruttore
            potential_infected.append(istruttore)

        for p in prenotazioni:
            potential_infected.append(p.IDCliente)
    return [get_persona_by_cf(cf) for cf in (list(set(potential_infected)))]


def get_prenotazioni_persona(cf, mese, anno):
    q = session_ospite.query(Prenotazione).filter(Prenotazione.IDCliente == cf,
                                                  extract('year', Prenotazione.Data) == anno,
                                                  extract('month', Prenotazione.Data) == mese).order_by(Prenotazione.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "prenotazione"
        del ret[-1]['_sa_instance_state']
    return ret


def get_all_prenotazioni_persona(cf):
    q = session_ospite.query(Prenotazione).filter(Prenotazione.IDCliente == cf,
                                                  Prenotazione.Data >= date.today(),
                                                  Prenotazione.OraInizio > time()).order_by(Prenotazione.Data, Prenotazione.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "prenotazione"
        del ret[-1]['_sa_instance_state']
    return ret


def get_corsi_seguiti(persona):
    sub = session_utente.query(CorsoSeguito.Nome).filter(CorsoSeguito.IDCliente == persona)
    q = session_utente.query(Corso).filter(Corso.Nome.in_(sub)).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "corso"
        del ret[-1]['_sa_instance_state']
    return ret


def get_corsi_insegnante(cf, mese, anno):
    q = session_ospite.query(Corso).filter(Corso.IDIstruttore == cf,
                                           extract('year', Corso.Data) == anno,
                                           extract('month', Corso.Data) == mese).order_by(Corso.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "corso"
        del ret[-1]['_sa_instance_state']
    return ret


def insert_corso_seguito(persona, corso):
    to_add = CorsoSeguito(IDCliente=persona, Nome=corso)
    session_utente.add(to_add)
    session_utente.commit()


def delete_corso_seguito(persona, corso):
    q = delete(CorsoSeguito).where(CorsoSeguito.IDCliente == persona, CorsoSeguito.Nome == corso)
    session_utente.execute(q)
    session_utente.commit()


def is_seguito(persona, corso):
    if persona is not None and session_utente.query(CorsoSeguito).filter(CorsoSeguito.Nome == corso,
                                                                         CorsoSeguito.IDCliente == persona).count() > 0:
        return True
    return False


def crea_notifica(testo, mittente):
    notifica = Notifica(Testo=testo, Mittente=mittente)
    session_istruttore.add(notifica)
    session_istruttore.commit()
    return notifica


def invia_notifica(notifica, destinatari):
    for person in destinatari:
        if session_istruttore.query(Persona).filter(Persona.CF == person).first():
            to_add = NotificaDestinatario(IDNotifica=notifica.IDNotifica, Destinatario=person,
                                          Timestamp=datetime.now(), Letto=False)
            session_istruttore.add(to_add)
            session_istruttore.commit()


def get_notifiche_persona(cf):
    notify_ids = [i.IDNotifica for i in session_utente.query(NotificaDestinatario).filter(
        NotificaDestinatario.Destinatario == cf).all()]
    notifies = session_utente.query(Notifica).filter(Notifica.IDNotifica.in_(notify_ids)).all()
    inbox = []
    for notify in notifies:
        q = session_utente.query(NotificaDestinatario).filter(
            NotificaDestinatario.IDNotifica == notify.IDNotifica,
            NotificaDestinatario.Destinatario == cf).first()
        message = {'IDNotifica': notify.IDNotifica,
                   'Mittente': get_persona_by_cf(notify.Mittente).Email,
                   'Timestamp': q.Timestamp,
                   'Letto': q.Letto,
                   'Testo': notify.Testo}
        inbox.append(message)
    return inbox


def get_giorni_tracciamento():
    return session_utente.query(Generali).one().GiorniTracciamento
