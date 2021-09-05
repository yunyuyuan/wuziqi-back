from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '15ASDF3q$R#QHae574#RFQjw543qaGQ%#$HWB#'

tables = []
example = [
    {
        'id': 0,
        'player1': [[2, 3], [3, 5]],
        'player2': [[3, 3], [4, 2]],
        'create': 1594819641
    }
]


def start():
    from src import http_
    from src.socket_ import create_websocket

    app.run('127.0.0.1', port=6769)
    create_websocket(app).run(app, '127.0.0.1', port=6768)
