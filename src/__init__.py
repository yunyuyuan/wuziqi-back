from functools import wraps

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


def check_data(fn):
    @wraps(fn)
    def inner(data):
        if isinstance(data, dict):
            return fn(data)

    return inner


def find_table(create):
    try:
        return next(x for x in tables if x['create'] == create)
    except:
        return None


def is_player(table, secret):
    return secret in [table['player1']['secret'], table['player2']['secret']]


def is_winner(poses):
    win = False
    for pos in poses:
        # 水平向右
        if [pos[0] + 1, pos[1]] in poses and [pos[0] + 2, pos[1]] in poses and \
           [pos[0] + 3, pos[1]] in poses and [pos[0] + 4, pos[1]] in poses:
            win = True
            break
        # 垂直向下
        elif [pos[0], pos[1] + 1] in poses and [pos[0], pos[1] + 2] in poses and \
             [pos[0], pos[1] + 3] in poses and [pos[0], pos[1] + 4] in poses:
            win = True
            break
        # 斜向右下
        elif [pos[0] + 1, pos[1] + 1] in poses and [pos[0] + 2, pos[1] + 2] in poses and\
             [pos[0] + 3, pos[1] + 3] in poses and [pos[0] + 4, pos[1] + 4] in poses:
            win = True
            break
        # 斜向左下
        elif [pos[0] - 1, pos[1] + 1] in poses and [pos[0] - 2, pos[1] + 2] in poses and \
             [pos[0] - 3, pos[1] + 3] in poses and [pos[0] - 4, pos[1] + 4] in poses:
            win = True
            break
    return win
