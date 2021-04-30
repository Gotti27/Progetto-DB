# appF config options, read by appF.config.from_pyfile

DEBUG = False
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:0438@25.75.195.73:5432/palestra'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # resolve overhead problem

# TODO?: aggiungere queste opzioni di configurazione in futuro
# BCRYPT_LOG_ROUNDS = 12 # Configuration for the Flask-Bcrypt extension = number of hashing rounds
# MAIL_FROM_EMAIL = "robert@example.com" # For use in application emails
