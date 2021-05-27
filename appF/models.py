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
        del ret[-1]['_sa_instance_state']
    return ret


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
    return q.one()


def addTestPrenotazione():
    testAdd = Prenotazione(Data=date.today(), OraInizio=time(13, 0, 0), OraFine=time(15, 0, 0),
                           IDCliente="ABCDEFGHIJKLMNOP", IDSala=1)
    session.add(testAdd)
    session.commit()


def attiva_persona(persona):
    db.session.query(Persona).filter(Persona.CF == persona).update({'Attivo': True})
    db.session.commit()


def disattiva_persona(persona):
    db.session.query(Persona).filter(Persona.CF == persona).update({'Attivo': False})
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


def workout_book(persona, data, oraInizio, oraFine, sala, corso=None):
    # FIXME: non si possono usare and, or nella filter
    # todo: sostituire il quarto d'ora nei calcoli con l'intervallo deciso dal gestore
    approved = True
    day = int(datetime.date(datetime.strptime(str(data), '%Y-%m-%d')).weekday())
    # todo: segnalo mie bestemmie da elminare
    if oraInizio.split(':')[1] != '00' and oraInizio.split(':')[1] != '15' and oraInizio.split(':')[1] != '30' and \
            oraInizio.split(':')[1] != '45' or oraFine.split(':')[1] != '00' and oraFine.split(':')[1] != '15' and \
            oraFine.split(':')[1] != '30' and oraFine.split(':')[1] != '45':
        print("Porcodio ci stanno hackerando")
        return None
    my_time = []  # lista dei quarti d'ora = tempoDiApertura * 4
    giorni_festivi = db.session.query(GiornoFestivo).filter(GiornoFestivo.Giorno == data).first()
    if giorni_festivi is not None and (oraInizio < giorni_festivi.Apertura or oraFine > giorni_festivi.Chiusura):
        return None
    giorni_feriali = db.session.query(OrarioPalestra).filter(OrarioPalestra.GiornoSettimana == day).first()

    if oraInizio < str(giorni_feriali.Apertura) or oraFine > str(giorni_feriali.Chiusura):
        return None

    if corso == '':
        max_number = db.session.query(Sala).filter(Sala.IDSala == sala).first().MaxPersone
        available = db.session.query(Prenotazione).filter(Prenotazione.Data == data and Prenotazione.OraFine > oraInizio
                                                          and Prenotazione.OraInizio < oraFine and
                                                          Prenotazione.Sala == sala and Prenotazione.Approvata).all()
        apertura = int(
            int(str(giorni_feriali.Apertura).split(':')[0]) * 4 + int(str(giorni_feriali.Apertura).split(':')[1]) / 15)
        chiusura = int(
            int(str(giorni_feriali.Chiusura).split(':')[0]) * 4 + int(str(giorni_feriali.Chiusura).split(':')[1]) / 15)
        for _ in range(apertura, chiusura):
            my_time.append(0)
        for booked in available:
            start = (int(str(booked.OraInizio).split(':')[0]) - apertura) * 4 + (
                    int(str(booked.OraInizio).split(':')[1]) / 15)
            end = (int(str(booked.OraFine).split(':')[0]) - apertura) * 4 + int(str(booked.OraFine).split(':')[1]) / 15
            for t in range(int(start), int(end)):
                my_time[t] += 1
        for t in my_time:
            if max_number - t < 1:
                approved = False
                break
        new_book = Prenotazione(Data=data, OraInizio=oraInizio, OraFine=oraFine, IDCliente=persona.CF,
                                IDCorso=None, IDSala=sala, Approvata=approved)
    else:
        disponibilita_corso = db.session.query(Corso).filter(Corso.IDCorso == corso).first().MaxPersone
        if disponibilita_corso - numero_iscritti_corso(corso) < 1:
            approved = False
        new_book = Prenotazione(Data=data, OraInizio=oraInizio, OraFine=oraFine, IDCliente=persona.CF,
                                IDCorso=corso, IDSala=sala, Approvata=approved)
    session.add(new_book)
    session.commit()
    return new_book


def contact_tracing(zero, giorni):
    """
    rudimentale algoritmo di contact tracing che prende in input un positivo e un numero di giorni da analizzare
    e ritorna una lista di potenziali positivi
    TODO: testare su corsi e istruttori

    :param zero: positivo iniziale
    :param giorni: numero di giorni che si vuole prendere in considerazione (max=7)
    :return: lista di potenziali positivi
    """
    potential_infected = []
    giorni = int(giorni)
    if giorni > 7:
        giorni = 7

    last_zero_appearance_date = db.session.query(Prenotazione).filter(
        Prenotazione.IDCliente == zero.CF, Prenotazione.Data <= datetime.today(),
        Prenotazione.Approvata == true()).order_by(Prenotazione.Data.desc()).first()
    if last_zero_appearance_date is not None:
        last_zero_appearance_date = last_zero_appearance_date.Data
    else:
        return []
    lower_limit_date = last_zero_appearance_date - timedelta(days=giorni)
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

    potential_infected_distinct = set(potential_infected)
    potential_infected = []
    for person in potential_infected_distinct:
        potential_infected.append(get_persona_by_cf(person))

    return potential_infected
