from flask_socketio import SocketIO
from flask import request
from src import app

socket_io = SocketIO(app, cors_allowed_origins='*')


@socket_io.on('connect', namespace='/*')
def connect(auth):
    print('connect')
    pass


@socket_io.on('disconnect', namespace='/*')
def disconnect():
    print('disconnect', request.url)
    pass


@socket_io.on('json', namespace='/*')
def json(data):
    print('json', data)
    pass

