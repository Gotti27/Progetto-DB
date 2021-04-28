from sqlalchemy import create_engine

print("Hello World!")

DATABASE_URI = 'postgres+psycopg2://campa:1234@localhost:5432/Progetto-DB'

engine = create_engine(DATABASE_URI)
