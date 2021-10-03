import time
from functools import wraps
from threading import Event
from config import cors_origin

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = '15ASDF3q$R#QHae574#RFQjw543qaGQ%#$HWB#'
app.debug = True
app.template_folder = '../templates'
app.static_folder = '../static'

lock = Event()
lock.set()
CORS(app, origins=cors_origin)

tables = []


def start():
    from src import http_
    from src import socket_
    socket_.socket_io.run(app, host='0.0.0.0', port=6768)


# 检查参数是否合法
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


# 检查是不是玩家发送的请求
def is_player(table, secret):
    for p in [table['player1'], table['player2']]:
        if secret == p['secret']:
            return p
    return False


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


# 判断游戏结束
def dedicate_game_end(socketio):
    while 1:
        socketio.sleep(0.2)
        time_now = time.time()
        for t in tables:
            last_put = t['last_put']
            if last_put > 0 and time_now - last_put > 30:
                # 超时
                if lock.wait(10):
                    lock.clear()
                    socketio.emit('game_end', {'type': -2}, to=t['create'])
                    tables.remove(t)
                    socketio.close_room(t['create'])
                    lock.set()
