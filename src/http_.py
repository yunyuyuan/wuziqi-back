from src import app, tables, find_table, lock
from flask import jsonify, request
from time import time
from secrets import token_hex

from src.socket_ import socket_io


@app.route('/get_table', methods=['post'])
def get_table():
    return jsonify(list(map(lambda item: {
            'player1': {
                'nick': item['player1']['nick'],
                'avatar': item['player1']['avatar']
            },
            'player2': {
                'nick': item['player2']['nick'],
                'avatar': item['player2']['avatar']
            },
            'create': item['create']
        }, tables)))


@app.route('/create_table', methods=['post'])
def create():
    if lock.wait(10):
        lock.clear()
        params = request.get_json() or {}
        new_table = {
            'player1': {
                'nick': params.get('nick', '无名高手'),
                'secret': token_hex(16),
                'avatar': params.get('avatar', 'dog'),
                'piece': []
            },
            'player2': {
                'nick': None,
                'secret': token_hex(16),
                'avatar': 'dog',
                'piece': []
            },
            'create': int(time()*1000),
            'watch': [],
            'last_put': 0
        }
        tables.append(new_table)
        lock.set()
        return jsonify({
            'create': new_table['create'],
            'secret': new_table['player1']['secret']
        })
    else:
        return jsonify({
            'err': True,
            'msg': '未找到该房间'
        })


@app.route('/join_table', methods=['post'])
def join():
    if lock.wait(10):
        lock.clear()
        params = request.get_json() or {}
        create_ = params.get('create', 0)
        found = find_table(create_)
        if found:
            lock.set()
            player2 = params.get('nick', '无名高手')
            if found['player2']['nick'] is not None:
                lock.set()
                return jsonify({
                    'err': True,
                    'msg': '已经有人加入了'
                })
            found['player2']['nick'] = player2
            found['player2']['avatar'] = params.get('avatar', 'dog')
            found['last_put'] = time()
            socket_io.emit('game_start', {'player2': {'nick': player2, 'avatar': found['player2']['avatar']}}, to=create_)
            lock.set()
            return jsonify({
                'player1': {'nick': found['player1']['nick'], 'avatar': found['player1']['avatar']},
                'secret': found['player2']['secret']
            })
        lock.set()
        return jsonify({
            'err': True,
            'msg': '未找到该房间'
        })
    else:
        return jsonify({
            'err': True,
            'msg': '服务器繁忙'
        })


@app.route('/watch_table', methods=['post'])
def watch():
    params = request.get_json() or {}
    create_ = params.get('create', 0)
    found = find_table(create_)
    if found:
        return jsonify({
            'type': True,
            'player1': {
                'piece': found['player1']['piece'],
                'nick': found['player1']['nick']
            },
            'player2': {
                'piece': found['player2']['piece'],
                'nick': found['player2']['nick']
            },
            'secret': token_hex(16),
            'watch': len(found['watch'])
        })
    return jsonify({
        'err': True,
        'msg': '未找到该房间'
    })
