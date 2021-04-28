from main import db
from sqlalchemy import *
from sqlalchemy.orm import *

DATABASE_URI = 'postgresql://campa:1234@25.75.195.73:5432/palestra'
engine = create_engine(DATABASE_URI)

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


Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()

def addTestElement():
    testAdd = Sala(IDSala=1, MaxPersone=50, Tipo="Test2")
    session.add(testAdd)
    session.commit()

def getSale():
    testQuery = db.session.query(Sala).all()   # qui è necessario salvare la pending instance
    return testQuery
