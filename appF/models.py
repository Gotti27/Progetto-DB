from run import db, engine
from sqlalchemy import *
from sqlalchemy.orm import *

Base = declarative_base()  # tabella = classe che eredita da Base


class Sala(Base):
    __tablename__ = 'Sale'  # obbligatorio

    IDSala = Column(Integer, primary_key=True)  # almeno un attributo deve fare parte della primary key
    MaxPersone = Column(SmallInteger)
    Tipo = Column(Text)
    IDCodaTesta = Column(Integer)
    IDCodaCoda = Column(Integer)

    # questo metodo è opzionale, serve solo per pretty printing
    def __repr__(self):
        return "<Sala(ID='%s', MaxP='%s', Tipo='%s')>" % (self.IDSala, self.MaxPersone, self.Tipo)


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
    Telefono = Column(TEXT)
    Attivo = Column(BOOLEAN, nullable=False)

    def __repr__(self):
        return "<Persona: CF='%s', N='%s', C='%s', S='%s', DN='%s', Email='%s', PW='%s', Tel='%s', Act='%s'>" % (self.CF, self.Nome, self.Cognome, self.Sesso, self.DataNascita, self.Email, self.Password, self.Telefono, self.Attivo)


# TODO: Classi senza FK: PacchettiCorsi, Palestra

# TODO: Classi con FK: Clienti, Staff, Corsi, Prenotazioni


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()


def addTestElement():
    testAdd = Sala(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()


def getSale():
    testQuery = db.session.query(Sala).all()   # qui è necessario salvare la pending instance
    return testQuery
