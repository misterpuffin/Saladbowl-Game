from flask import Flask, render_template, session
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "")
socketio = SocketIO(app, manage_session=False)

from app import routes, sockets

