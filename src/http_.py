from src import app, tables
from flask import jsonify, request
from flask_cors import CORS
from threading import Event
from time import time
from secrets import token_hex

from src.socket_ import socket_io

lock = Event()
lock.set()
CORS(app)


@app.route('/get_table', methods=['post'])
def get_table():
    return jsonify(list(map(lambda item: {
            'player1': {
                'nick': item['player1']['nick']
            },
            'player2': {
                'nick': item['player2']['nick']
            },
            'create': item['create']
        }, tables)))


@app.route('/create_table', methods=['post'])
def create():
    result = lock.wait(10)
    if result:
        lock.clear()
        params = request.get_json() or {}
        new_table = {
            'player1': {
                'nick': params.get('nick', '无名高手'),
                'secret': token_hex(16),
                'piece': []
            },
            'player2': {
                'nick': None,
                'secret': token_hex(16),
                'piece': []
            },
            'create': int(time()*1000)
        }
        tables.append(new_table)
        lock.set()
        return jsonify({
            'create': new_table['create'],
            'secret': new_table['player1']['secret']
        })
    else:
        return jsonify(False)


@app.route('/join_table', methods=['post'])
def join():
    result = lock.wait(10)
    if result:
        lock.clear()
        params = request.get_json() or {}
        create_ = params.get('create', 0)
        found = None
        for item in tables:
            if item['create'] == create_:
                found = item
                break
        lock.set()
        player2 = params.get('nick', '无名高手')
        found['player2']['nick'] = player2
        socket_io.emit('game_start', {'player2': player2}, namespace='/'+str(create_))
        return jsonify({
            'player1': found['player1']['nick'],
            'secret': found['player2']['secret']
        })
    else:
        return jsonify(False)
