from run import db, engine
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import *

Base = declarative_base()  # tabella = classe che eredita da Base


class Sale(Base):
    __tablename__ = 'sale'

    IDSala = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    Tipo = Column(TEXT, nullable=True)

    def __repr__(self):
        return "<Sala: ID='%s', MaxP='%s', Tipo='%s'>" % (self.IDSala, self.MaxPersone, self.Tipo)


class Persone(Base):
    __tablename__ = 'persone'

    CF = Column(VARCHAR, primary_key=True)
    Nome = Column(VARCHAR, nullable=False)
    Cognome = Column(VARCHAR, nullable=False)
    Sesso = Column('Sesso', Enum('M', 'F'), nullable=False)
    DataNascita = Column(DATE, nullable=False)
    Email = Column(TEXT, nullable=False, unique=True)
    Password = Column(TEXT, nullable=False)
    Telefono = Column(TEXT, nullable=True)
    Attivo = Column(BOOLEAN, nullable=False)

    '''
        per la questione di rappresentare il Sesso
        #https://docs.sqlalchemy.org/en/14/core/type_basics.html?highlight=enum#sqlalchemy.types.Enum
        https://stackoverflow.com/questions/20644292/how-to-create-enum-in-sqlalchemy/20646024
    '''

    def __repr__(self):
        return "<Persona: CF='%s', N='%s', C='%s', S='%s', DN='%s', Email='%s', PW='%s', Tel='%s', Act='%s'>" % (self.CF, self.Nome, self.Cognome, self.Sesso, self.DataNascita, self.Email, self.Password, self.Telefono, self.Attivo)


class PacchettiCorsi(Base):
    __tablename__ = 'pacchettiCorsi'

    IDPacchetto = Column(INTEGER, primary_key=True)
    Nome = Column(TEXT, nullable=False)
    Descrizione = Column(TEXT, nullable=True)

    def __repr__(self):
        return "<PacchettiCorsi: ID='%s', N='%s', Des='%s'>" % (self.IDPacchetto, self.Nome, self.Descrizione)


class OrariPalestra(Base):
    __tablename__ = 'orariPalestra'

    Apertura = Column(DATE, primary_key=True)
    Chiusura = Column(DATE, primary_key=True)
    GiornoSettimana = Column(INTEGER, nullable=False)

    def __repr__(self):
        return "<Palestra: A='%s', C='%s', Day='%s>" % (self.Apertura, self.Chiusura, self.GiornoSettimana)


class GiorniFestivi(Base):
    __tablename__ = 'giorniFestivi'

    IDGiorno = Column(INTEGER, primary_key=True)
    Apertura = Column(TIME, nullable=True)
    Chiusura = Column(TIME, nullable=True)
    Giorno = Column(DATE, nullable=False)


class Clienti(Base):
    __tablename__ = 'clienti'

    IDCliente = Column(VARCHAR, ForeignKey(Persone.CF), primary_key=True)
    DataIscrizione = Column(DATE, nullable=False)
    PagamentoMese = Column(BOOLEAN, nullable=False)

    persone = relationship(Persone, uselist=False)

    # TODO: pretty printing


class Staff(Base):
    __tablename__ = 'staff'

    IDStaff = Column(VARCHAR, ForeignKey(Persone.CF), primary_key=True)
    Ruolo = Column('Ruolo', Enum('Istruttore', 'Gestore'), nullable=False)

    persone = relationship(Persone, uselist=False)

    # TODO: pretty printing


class Corsi(Base):
    __tablename__ = 'corsi'

    IDCorso = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    IDSala = Column(INTEGER, ForeignKey(Sale.IDSala), nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    Data = Column(DATE, nullable=False)
    IDPaccheto = Column(INTEGER, ForeignKey(PacchettiCorsi.IDPacchetto))
    Descrizione = Column(TEXT, nullable=True)
    IDIstruttore = Column(VARCHAR, ForeignKey(Staff.IDStaff), nullable=False)

    sale = relationship(Sale, uselist=False)
    pacchettiCorsi = relationship(PacchettiCorsi, uselist=False)
    staff = relationship(Staff, uselist=False)

    # TODO: pretty printing


class Prenotazioni(Base):
    __tablename__ = 'prenotazioni'

    IDPrenotazione = Column(INTEGER, primary_key=True)
    Data = Column(DATE, nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    IDCliente = Column(VARCHAR, ForeignKey(Clienti.IDCliente), nullable=False)
    IDCorso = Column(INTEGER, ForeignKey(Corsi.IDCorso))
    IDSala = Column(INTEGER, ForeignKey(Sale.IDSala), nullable=False)
    Approvata = Column(BOOLEAN, nullable=False)

    clienti = relationship(Clienti, uselist=False)
    corsi = relationship(Corsi, uselist=False)
    sale = relationship(Sale, uselist=False)

    # TODO: pretty printing


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()


def addTestSala():
    testAdd = Sale(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()

def addTestPersona():
    print("\t addPersona")
    testAdd = Persone(CF="ABCDEFGHIJKLMNOP", Nome="Mario", Cognome="Rossi", Sesso="M", DataNascita=date.today(), Email="ciao@ciao.ciao", Password="1234", Attivo=True)
    session.add(testAdd)
    session.commit()

def addTestCliente():
    addTestPersona()
    print("\t addCliente")
    testAdd = Clienti(IDCliente="ABCDEFGHIJKLMNOP", DataIscrizione=date.today(), PagamentoMese=False)
    session.add(testAdd)
    session.commit()

def getSale():
    testQuery = db.session.query(Sale).all()   # qui è necessario salvare la pending instance
    return testQuery
