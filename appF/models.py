from run import db, engine
from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import *

Base = declarative_base()  # tabella = classe che eredita da Base


class Sale(Base):
    __tablename__ = 'sale'

    IDSala = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    Tipo = Column(TEXT)

    def __repr__(self):
        return "<Sala: ID='%s', MaxP='%s', Tipo='%s'>" % (self.IDSala, self.MaxPersone, self.Tipo)


class Persone(Base):
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
    Descrizione = Column(TEXT)

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
    Apertura = Column(TIME)
    Chiusura = Column(TIME)
    Giorno = Column(DATE, nullable=False)


class Clienti(Base):
    __tablename__ = 'clienti'

    IDCliente = Column(CHAR(16), ForeignKey(Persone.CF), primary_key=True)
    DataIscrizione = Column(DATE, nullable=False)
    PagamentoMese = Column(BOOLEAN, nullable=False)

    persone = relationship(Persone, uselist=False)

    def __repr__(self):
        return "<Clienti: ID:'%s', DatIscr:'%s', PagMese:'%s'>" % (self.IDCliente, self.DataIscrizione, self.PagamentoMese)
    

class Staff(Base):
    __tablename__ = 'staff'

    IDStaff = Column(CHAR(16), ForeignKey(Persone.CF), primary_key=True)
    Ruolo = Column('Ruolo', Enum('Istruttore', 'Gestore'), nullable=False)

    persone = relationship(Persone, uselist=False)

    def __repr__(self):
        return "<Staff: ID:'%s', Role:'%s'>" % (self.IDStaff, self.Ruolo)


class Corsi(Base):
    __tablename__ = 'corsi'

    IDCorso = Column(INTEGER, primary_key=True)
    MaxPersone = Column(SMALLINT, nullable=False)
    IDSala = Column(INTEGER, ForeignKey(Sale.IDSala), nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    Data = Column(DATE, nullable=False)
    Descrizione = Column(TEXT)
    Nome = Column(VARCHAR, nullable=False)
    IDPacchetto = Column(INTEGER, ForeignKey(PacchettiCorsi.IDPacchetto))
    IDIstruttore = Column(CHAR(16), ForeignKey(Staff.IDStaff), nullable=False)

    sale = relationship(Sale, uselist=False)
    pacchettiCorsi = relationship(PacchettiCorsi, uselist=False)
    staff = relationship(Staff, uselist=False)

    def __repr__(self):
        return "<ID:%s, Nome:%s, Max:%s, IDSala:%s, OInizio:%s, OFine:%s, Data:%s, Descr:%s, IDPac:%s, IDIstr:%s>" % (self.IDCorso, self.Nome, self.MaxPersone, self.IDSala, self.OraInizio, self.OraFine, self.Data, str(self.Descrizione), str(self.IDPacchetto), self.IDIstruttore)


class Prenotazioni(Base):
    __tablename__ = 'prenotazioni'

    IDPrenotazione = Column(INTEGER, primary_key=True)
    Data = Column(DATE, nullable=False)
    OraInizio = Column(TIME, nullable=False)
    OraFine = Column(TIME, nullable=False)
    IDCliente = Column(VARCHAR, ForeignKey(Clienti.IDCliente), nullable=False)
    IDCorso = Column(INTEGER, ForeignKey(Corsi.IDCorso))
    IDSala = Column(INTEGER, ForeignKey(Sale.IDSala), nullable=False)
    Approvata = Column(BOOLEAN, nullable=False, default=True)

    clienti = relationship(Clienti, uselist=False)
    corsi = relationship(Corsi, uselist=False)
    sale = relationship(Sale, uselist=False)

    def __repr__(self):
        return "<Prenotazioni: ID:'%s', Data:'%s', OInizio:'%s', OFine:'%s', IDCliente:'%s', IDCorso:'%s', IDSala:'%s', Aprr:'%s'>" % (self.IDPrenotazione, self.Data, self.OraInizio, self.OraFine, self.IDCliente, self.IDCorso, self.IDSala, self.Approvata)


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()

def insert_persona(cf, nome, cognome, sesso, data_nascita, email, password, attivo, telefono=None):
    to_add = Persone(CF=cf, Nome=nome, Cognome=cognome, Sesso=sesso, DataNascita=data_nascita, Email=email, Password=password, Attivo=attivo, Telefono=telefono)
    session.add(to_add)
    session.commit()
    return toAdd


def insert_cliente(persona):
    to_add = Clienti(IDCliente=persona.CF, DataIscrizione=date.today(), PagamentoMese=False)
    session.add(to_add)
    session.commit()


def insert_istruttore(persona):
    to_add = Staff(IDStaff=persona.CF, Ruolo='Istruttore')
    session.add(to_add)
    session.commit()


def insert_corso(max_persone, id_sala, ora_inizio, ora_fine, data, id_istruttore, id_pacchetto=None, descrizione=None):
    to_add = Corsi(MaxPersone=max_persone, IDSala=id_sala, OraInizio=ora_inizio, OraFine=ora_fine, Data=data , IDIstruttore=id_istruttore, IDPacchetto=id_pacchetto, Descrizione=descrizione)
    session.add(to_add)
    session.commit()


def get_corsi(mese, anno):
    q = db.session.query(Corsi).all()
    return q


def addTestSala():
    testAdd = Sale(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()


def getSale():
    testQuery = db.session.query(Sale).all()   # qui è necessario salvare la pending instance
    return testQuery


def addTestPrenotazione():
    testAdd = Prenotazioni(Data=date.today(), OraInizio=time(13,0,0), OraFine=time(15,0,0), IDCliente="ABCDEFGHIJKLMNOP", IDSala=1)
    session.add(testAdd)
    session.commit()