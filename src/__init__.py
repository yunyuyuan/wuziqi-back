from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '15ASDF3q$R#QHae574#RFQjw543qaGQ%#$HWB#'
app.debug = True
app.template_folder = '../templates'
app.static_folder = '../static'

tables = []


def start():
    from src import http_
    from src import socket_

    socket_.socket_io.run(app, host='0.0.0.0', port=6768)
