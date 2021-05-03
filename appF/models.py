from run import db, engine
from sqlalchemy import *
from sqlalchemy.orm import *

Base = declarative_base()  # tabella = classe che eredita da Base


class Sala(Base):
    __tablename__ = 'Sale'

    IDSala = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    Tipo = Column(TEXT, nullable=True)
    IDCodaTesta = Column(INTEGER, nullable=True)
    IDCodaCoda = Column(INTEGER, nullable=True)

    def __repr__(self):
        return "<Sala: ID='%s', MaxP='%s', Tipo='%s'>" % (self.IDSala, self.MaxPersone, self.Tipo)


class Persone(Base):
    __tablename__ = 'Persone'

    CF = Column(VARCHAR, primary_key=True)
    Nome = Column(VARCHAR, nullable=False)
    Cognome = Column(VARCHAR, nullable=False)
    Sesso = Column('Sesso', Enum('M', 'F'), nullable=False)
    '''
    per la questione di rappresentare il Sesso
    #https://docs.sqlalchemy.org/en/14/core/type_basics.html?highlight=enum#sqlalchemy.types.Enum
    https://stackoverflow.com/questions/20644292/how-to-create-enum-in-sqlalchemy/20646024
    '''
    DataNascita = Column(DATE, nullable=False)
    Email = Column(TEXT, nullable=False)
    Password = Column(TEXT, nullable=False)
    Telefono = Column(TEXT, nullable=True)
    Attivo = Column(BOOLEAN, nullable=False)

    def __repr__(self):
        return "<Persona: CF='%s', N='%s', C='%s', S='%s', DN='%s', Email='%s', PW='%s', Tel='%s', Act='%s'>" % (self.CF, self.Nome, self.Cognome, self.Sesso, self.DataNascita, self.Email, self.Password, self.Telefono, self.Attivo)


class PacchettiCorsi(Base):
    __tablename__ = 'PacchettiCorsi'

    IDPacchetto = Column(INTEGER, primary_key=True)
    Nome = Column(TEXT, nullable=False)
    Descrizione = Column(TEXT, nullable=True)

    def __repr__(self):
        return "<PacchettiCorsi: ID='%s', N='%s', Des='%s'>" % (self.IDPacchetto, self.Nome, self.Descrizione)


class Palestra(Base):
    __tablename__ = 'Palestra'

    Apertura = Column(DATE, nullable=false)
    Chiusura = Column(DATE, nullable=false)

    def __repr__(self):
        return "<Palestra: A='%s', C='%s'>" % (self.Apertura, self.Chiusura)


class Clienti(Base):
    __tablename__ = 'Clienti'

    # TODO: IDCLiente
    DataIscrizione = Column(DATE, nullable=False)
    PagamentoMese = Column(BOOLEAN, nullable=False)

    # TODO: pretty printing


class Staff(Base):
    __tablename__ = 'Staff'

    # TODO: IDStaff
    Ruolo = Column('Ruolo', Enum('Istruttore', 'Gestore'), nullable=False)

    # TODO: pretty printing


class Corsi(Base):
    __tablename__ = 'Corsi'

    IDCorso = Column(INTEGER, pimary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    # TODO:IDSala
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    Data = Column(DATE, nullable=False)
    # TODO:IDPaccheto
    Descrizione = Column(TEXT, nullable=True)
    # TODO:IDIStruttore

    # TODO: pretty printing


class Prenotazioni(Base):
    __tablename__ = 'Prenotazioni'

    IDPrenotazione = Column(INTEGER, primary_key=True)
    Data = Column(DATE, nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    # TODO:IDCliente
    # TODO:IDCorso
    # TODO:IDSala
    Approvata = Column(BOOLEAN, nullable=False)

    # TODO: pretty printing


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()


def addTestElement():
    testAdd = Sala(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()


def getSale():
    testQuery = db.session.query(Sala).all()   # qui è necessario salvare la pending instance
    return testQuery
