from flask import Flask
from flask_session import Session


app = Flask(__name__)

app.secret_key = "clavesecretadeAna"
# Configuración de flask_session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = True

Session(app)

BASE_DE_DATOS = "private_wall"