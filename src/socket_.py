from flask_socketio import SocketIO


def create_websocket(app):
    socket_io = SocketIO(app)
    return socket_io
