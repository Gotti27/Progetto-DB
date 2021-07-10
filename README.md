# Progetto-DB
Web application to manage a gym during covid-19, so there are for instance tools for online booking and to perform contact tracing. The project is developed with flask-sqlalchemy backend and runs on postgresql db. We reccomend to read documentation.pdf, in particular the db-diagram.

`FLASK_APP=run.py`\
`flask run`


## Link DB Schema
https://docs.google.com/spreadsheets/d/11KIOxlNzZyOvWzAp3gcyVts9LM_70kXUfcY_hgRxfbg/edit#gid=0

## Files and directories
templates/ &#8594; file html \
static/    &#8594; file css e js \
instance/  &#8594; file di configurazione al di fuori del version control \
appF/      &#8594; collegamento con DB (models.py) e flask (views.py) \
config.py  &#8594; impostazioni di configurazione \
run.py     &#8594; "main"
