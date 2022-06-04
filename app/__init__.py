from flask import Flask, render_template, session
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "")
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
socketio = SocketIO(app, manage_session=False)
print("Server starting on port: 5000")

from app import routes, sockets

