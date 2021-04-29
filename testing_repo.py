from sqlalchemy import create_engine

print("Hello World!")

DATABASE_URI = 'postgresql://campa:1234@25.75.195.73:5432/palestra'

engine = create_engine(DATABASE_URI)
