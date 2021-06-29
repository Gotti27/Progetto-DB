import datetime

from run import db, engine
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import *
from flask_login import UserMixin

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

    def get_id(self):
        return self.CF

    @property
    def get_email(self):
        return str(self.Email)

    def is_admin(self):
        return (db.session.query(Staff).filter(Staff.IDStaff == self.CF).filter(Staff.Ruolo == 'Gestore')).count() > 0

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


Session = sessionmaker(bind=engine)  # creazione della factory
session = Session()


def insert_persona(cf, nome, cognome, sesso, data_nascita, email, password, attivo, telefono=None):
    to_add = Persona(CF=cf, Nome=nome, Cognome=cognome, Sesso=sesso, DataNascita=data_nascita, Email=email,
                     Password=password, Attivo=attivo, Telefono=telefono)
    session.add(to_add)
    session.commit()
    return to_add


def insert_cliente(persona):
    to_add = Cliente(IDCliente=persona.CF, DataIscrizione=date.today(), PagamentoMese=False)
    session.add(to_add)
    session.commit()


def insert_istruttore(persona):
    to_add = Staff(IDStaff=persona.CF, Ruolo='Istruttore')
    session.add(to_add)
    session.commit()


def insert_corso(max_persone, min_persone, id_sala, ora_inizio, ora_fine, data, id_istruttore, nome, descrizione=None):
    c = Corso(MaxPersone=max_persone, MinPersone=min_persone, IDSala=id_sala, OraInizio=ora_inizio, OraFine=ora_fine,
              Data=data, IDIstruttore=id_istruttore, Descrizione=descrizione, Nome=nome)
    session.add(c)
    session.commit()


def get_corsi(mese, anno):
    q = db.session.query(Corso).filter(extract('year', Corso.Data) == anno).filter(
        extract('month', Corso.Data) == mese).order_by(Corso.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "corso"
        del ret[-1]['_sa_instance_state']
    return ret


def get_corsi_futuri():
    q = db.session.query(Corso).filter(Corso.Data >= date.today()).filter(Corso.OraInizio > time()).order_by(
        Corso.Data).all()
    return q


def get_corso_by_id(id):
    q = db.session.query(Corso).filter(Corso.IDCorso == id).first()
    return q.__dict__


def numero_iscritti_corso(corso):
    iscr = db.session.query(Prenotazione).filter(Prenotazione.IDCorso == corso).filter(Prenotazione.Approvata).count()
    return iscr


def get_sale():
    q = db.session.query(Sala).all()
    return q


def get_istruttori():
    q = db.session.query(Staff.IDStaff, Persona.Nome, Persona.Cognome).filter(Staff.Ruolo == "Istruttore",
                                                                              Persona.CF == Staff.IDStaff).all()
    return q


def get_persona_by_email(email):
    q = db.session.query(Persona).filter(Persona.Email == email)
    return q.one()


def get_persona_by_cf(cf):
    q = db.session.query(Persona).filter(Persona.CF == cf)
    return q.first()


def attiva_persona(persona):
    db.session.query(Persona).filter(Persona.CF == persona).update({'Attivo': True})
    db.session.commit()


def disattiva_persona(persona):
    db.session.query(Persona).filter(Persona.CF == persona).update({'Attivo': False})
    db.session.query(Prenotazione).filter(Prenotazione.IDCliente == persona,
                                          Prenotazione.Data >= datetime.today()#,
                                          #Prenotazione.OraInizio >= datetime.now())\
                                          ).update({'Approvata': False})
    db.session.commit()


def setta_pagante(cliente):
    db.session.query(Cliente).filter(Cliente.IDCliente == cliente).update({'PagamentoMese': True})
    db.session.commit()


def setta_non_pagante(cliente):
    db.session.query(Cliente).filter(Cliente.IDCliente == cliente).update({'PagamentoMese': False})
    db.session.commit()


def insert_sala(max_persone, tipo):
    to_add = Sala(MaxPersone=max_persone, Tipo=tipo)
    session.add(to_add)
    session.commit()


def get_time_step():
    q = db.session.query(Generali).one().MinutiScaglioni
    return q


def get_prenotazione_by_id(id):
    q = db.session.query(Prenotazione).filter(Prenotazione.IDPrenotazione == id).first()
    return q.__dict__


def insert_prenotazione(persona, data, ora_inizio, ora_fine, sala, corso=None):
    approved = True
    day = int(datetime.date(datetime.strptime(str(data), '%Y-%m-%d')).weekday())
    time_step = get_time_step()
    # TODO: segnalo mie bestemmie da elminare
    if int(str(ora_inizio).split(':')[1]) % time_step != 0 or int(str(ora_fine).split(':')[1]) % time_step != 0:
        print("Porcodio ci stanno hackerando")
        return None

    orari_giorno = db.session.query(GiornoFestivo).filter(GiornoFestivo.Giorno == data).first()
    if orari_giorno is None:
        orari_giorno = db.session.query(OrarioPalestra).filter(OrarioPalestra.GiornoSettimana == day).first()

    if orari_giorno is None or datetime.strptime(str(ora_inizio)[0:-3], '%H:%M').time() < orari_giorno.Apertura or datetime.strptime(str(ora_fine)[0:-3], '%H:%M').time() > orari_giorno.Chiusura:
        return None

    if corso == '':
        max_number = db.session.query(Sala).filter(Sala.IDSala == sala).first().MaxPersone
        available = db.session.query(Prenotazione).filter(Prenotazione.Data == data, Prenotazione.OraFine > ora_inizio,
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
        disponibilita_corso = db.session.query(Corso).filter(Corso.IDCorso == corso).first().MaxPersone
        if disponibilita_corso - numero_iscritti_corso(corso) < 1:
            approved = False
        new_book = Prenotazione(Data=data, OraInizio=ora_inizio, OraFine=ora_fine, IDCliente=persona.CF,
                                IDCorso=corso, IDSala=sala, Approvata=approved)
    session.add(new_book)
    session.commit()
    return new_book


def delete_prenotazione(persona, corso):
    q = delete(Prenotazione).where(Prenotazione.IDCliente == persona, Prenotazione.IDCorso == corso)
    session.execute(q)
    session.commit()


def is_iscritto(persona, corso):
    if persona is not None and db.session.query(Prenotazione).filter(Prenotazione.IDCliente == persona,
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

    last_zero_appearance_date = db.session.query(Prenotazione).filter(
        Prenotazione.IDCliente == zero.CF, Prenotazione.Data <= datetime.today(),
        Prenotazione.Approvata == true()).order_by(Prenotazione.Data.desc()).first()
    if last_zero_appearance_date is not None:
        last_zero_appearance_date = last_zero_appearance_date.Data
    else:
        return []
    lower_limit_date = last_zero_appearance_date - timedelta(days=days)
    last_zero_appearances = db.session.query(Prenotazione) \
        .filter(Prenotazione.IDCliente == zero.CF, Prenotazione.Data >= lower_limit_date,
                Prenotazione.Approvata == true()).order_by(Prenotazione.Data.desc()).all()

    for appearance in last_zero_appearances:
        prenotazioni = db.session.query(Prenotazione).filter(
            Prenotazione.Data == appearance.Data, Prenotazione.IDSala == appearance.IDSala,
            or_(Prenotazione.OraFine >= appearance.OraInizio, Prenotazione.OraInizio <= appearance.OraFine),
            Prenotazione.Approvata == true()).all()

        if appearance.IDCorso is not None:
            istruttore = db.session.query(Corso).filter(Corso.IDCorso == appearance.IDCorso).first().IDIstruttore
            potential_infected.append(istruttore)

        for p in prenotazioni:
            potential_infected.append(p.IDCliente)
    return [get_persona_by_cf(cf) for cf in (list(set(potential_infected)))]


def get_prenotazioni_persona(cf, mese, anno):
    q = db.session.query(Prenotazione).filter(Prenotazione.IDCliente == cf).filter(
        extract('year', Prenotazione.Data) == anno).filter(
        extract('month', Prenotazione.Data) == mese).order_by(Prenotazione.OraInizio).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "prenotazione"
        del ret[-1]['_sa_instance_state']
    return ret


def get_corsi_seguiti(persona):
    sub = db.session.query(CorsoSeguito.Nome).filter(CorsoSeguito.IDCliente == persona)
    q = db.session.query(Corso).filter(Corso.Nome.in_(sub)).all()
    ret = []
    for i in q:
        ret.append({property: str(value) for property, value in vars(i).items()})
        ret[-1]["type"] = "corso"
        del ret[-1]['_sa_instance_state']
    return ret


def insert_corso_seguito(persona, corso):
    to_add = CorsoSeguito(IDCliente=persona, Nome=corso)
    session.add(to_add)
    session.commit()


def delete_corso_seguito(persona, corso):
    q = delete(CorsoSeguito).where(CorsoSeguito.IDCliente == persona, CorsoSeguito.Nome == corso)
    session.execute(q)
    session.commit()


def is_seguito(persona, corso):
    if persona is not None and db.session.query(CorsoSeguito).filter(CorsoSeguito.Nome == corso,
                                                                     CorsoSeguito.IDCliente == persona).count() > 0:
        return True
    return False


def crea_notifica(testo, mittente):
    notifica = Notifica(Testo=testo, Mittente=mittente)
    session.add(notifica)
    session.commit()
    return notifica


def invia_notifica(notifica, destinatari):
    #notifica = crea_notifica(testo=testo, mittente=mittente)
    for person in destinatari:
        to_add = NotificaDestinatario(IDNotifica=notifica.IDNotifica, Destinatario=person,
                                      Timestamp=datetime.now(), Letto=False)
        session.add(to_add)
        session.commit()
