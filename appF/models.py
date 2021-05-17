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
        return "<Persona: CF='%s', N='%s', C='%s', S='%s', DN='%s', Email='%s', PW='%s', Tel='%s', Act='%s'>" % (self.CF, self.Nome, self.Cognome, self.Sesso, self.DataNascita, self.Email, self.Password, self.Telefono, self.Attivo)


class PacchettoCorsi(Base):
    __tablename__ = 'pacchettiCorsi'

    IDPacchetto = Column(INTEGER, primary_key=True)
    Nome = Column(TEXT, nullable=False)
    Descrizione = Column(TEXT)

    def __repr__(self):
        return "<PacchettiCorsi: ID='%s', N='%s', Des='%s'>" % (self.IDPacchetto, self.Nome, self.Descrizione)


class OrarioPalestra(Base):
    __tablename__ = 'orariPalestra'

    Apertura = Column(DATE, primary_key=True)
    Chiusura = Column(DATE, primary_key=True)
    GiornoSettimana = Column(INTEGER, nullable=False)

    def __repr__(self):
        return "<Palestra: A='%s', C='%s', Day='%s>" % (self.Apertura, self.Chiusura, self.GiornoSettimana)


class GiornoFestivo(Base):
    __tablename__ = 'giorniFestivi'

    IDGiorno = Column(INTEGER, primary_key=True)
    Apertura = Column(TIME)
    Chiusura = Column(TIME)
    Giorno = Column(DATE, nullable=False)


class Cliente(Base):
    __tablename__ = 'clienti'

    IDCliente = Column(CHAR(16), ForeignKey(Persona.CF), primary_key=True)
    DataIscrizione = Column(DATE, nullable=False)
    PagamentoMese = Column(BOOLEAN, nullable=False)

    persone = relationship(Persona, uselist=False)

    def __repr__(self):
        return "<Clienti: ID:'%s', DatIscr:'%s', PagMese:'%s'>" % (self.IDCliente, self.DataIscrizione, self.PagamentoMese)
    

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
    IDSala = Column(INTEGER, ForeignKey(Sala.IDSala), nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    Data = Column(DATE, nullable=False)
    Descrizione = Column(TEXT)
    Nome = Column(VARCHAR, nullable=False)
    IDPacchetto = Column(INTEGER, ForeignKey(PacchettoCorsi.IDPacchetto))
    IDIstruttore = Column(CHAR(16), ForeignKey(Staff.IDStaff), nullable=False)

    sale = relationship(Sala, uselist=False)
    pacchettiCorsi = relationship(PacchettoCorsi, uselist=False)
    staff = relationship(Staff, uselist=False)

    def __repr__(self):
        return "<ID:%s, Nome:%s, Max:%s, IDSala:%s, OInizio:%s, OFine:%s, Data:%s, Descr:%s, IDPac:%s, IDIstr:%s>" % (self.IDCorso, self.Nome, self.MaxPersone, self.IDSala, self.OraInizio, self.OraFine, self.Data, str(self.Descrizione), str(self.IDPacchetto), self.IDIstruttore)


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
        return "<Prenotazioni: ID:'%s', Data:'%s', OInizio:'%s', OFine:'%s', IDCliente:'%s', IDCorso:'%s', IDSala:'%s', Aprr:'%s'>" %\
               (self.IDPrenotazione, self.Data, self.OraInizio, self.OraFine, self.IDCliente, self.IDCorso, self.IDSala, self.Approvata)


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()


def insert_persona(cf, nome, cognome, sesso, data_nascita, email, password, attivo, telefono=None):
    to_add = Persona(CF=cf, Nome=nome, Cognome=cognome, Sesso=sesso, DataNascita=data_nascita, Email=email, Password=password, Attivo=attivo, Telefono=telefono)
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


def insert_corso(max_persone, id_sala, ora_inizio, ora_fine, data, id_istruttore, id_pacchetto=None, descrizione=None):
    to_add = Corso(MaxPersone=max_persone, IDSala=id_sala, OraInizio=ora_inizio, OraFine=ora_fine, Data=data , IDIstruttore=id_istruttore, IDPacchetto=id_pacchetto, Descrizione=descrizione)
    session.add(to_add)
    session.commit()


def get_corsi(mese, anno):
    q = db.session.query(Corso).all()
    return q


def addTestSala():
    testAdd = Sala(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()


def get_sale():
    q = db.session.query(Sala).all()   # qui è necessario salvare la pending instance
    return q


def get_persona_by_email(email):
    q = db.session.query(Persona).filter(Persona.Email == email)
    return q.one()


def addTestPrenotazione():
    testAdd = Prenotazione(Data=date.today(), OraInizio=time(13,0,0), OraFine=time(15,0,0), IDCliente="ABCDEFGHIJKLMNOP", IDSala=1)
    session.add(testAdd)
    session.commit()