import time

from flask import session
from flask_socketio import SocketIO, join_room, emit, leave_room, close_room

from src import app, tables, find_table, check_data, is_player, is_winner, lock, dedicate_game_end

socket_io = SocketIO(app, cors_allowed_origins='*')
socket_io.background_started = False


@socket_io.on('connect')
def connect(auth):
    if not socket_io.background_started:
        socket_io.start_background_task(target=dedicate_game_end, socketio=socket_io)
        socket_io.background_started = True


@socket_io.on('disconnect')
def disconnect():
    try:
        create = session['room']
        secret = session['secret']
        player_leave(create, secret)
        leave_room(create)
        session['room'] = None
        session['secret'] = None
    except KeyError:
        pass


'''
'''


@check_data
@socket_io.on('join_room')
def join_room_(data):
    create = data.get('create', None)
    secret = data.get('secret', None)
    session['room'] = create
    session['secret'] = secret
    join_room(create)
    found_table = find_table(create)
    if found_table and secret and not is_player(found_table, secret):
        # 观战
        found_table['watch'].append(secret)
        emit('watcher_num_change', {'num': len(found_table['watch'])}, to=create)


@socket_io.on('cancel_create')
def cancel_create():
    create_ = session['room']
    found_table = find_table(create_)
    if found_table:
        if lock.wait(10):
            lock.clear()
            tables.remove(found_table)
            lock.set()


@check_data
@socket_io.on('leave_room')
def leave_room_():
    try:
        create = session['room']
        secret = session['secret']
        player_leave(create, secret)
        leave_room(create)
    except KeyError:
        pass


@check_data
@socket_io.on('put_chess')
def put_chess(data):
    try:
        create = session['room']
        secret = session['secret']
        pos = data.get('pos', [-1, -1])
        if pos[0] > -1:
            found_table = find_table(create)
            if found_table:
                player1 = found_table['player1']
                player2 = found_table['player2']
                current_player = player1
                player_num = 1
                if len(player1['piece']) != len(player2['piece']):
                    current_player = player2
                    player_num = 2
                if secret == current_player['secret']:
                    current_player['piece'].append(pos)
                    emit('chess_update', {'pos': pos}, to=create)
                    found_table['last_put'] = time.time()
                    # 检查获胜
                    if lock.wait(10):
                        lock.clear()
                        if is_winner(current_player['piece']):
                            emit('game_end', {'type': player_num}, to=create)
                            # 删除游戏
                            tables.remove(found_table)
                            close_room(create)
                        elif len(player1['piece']) == 113:
                            # 平手
                            emit('game_end', {'type': -1}, to=create)
                            # 删除游戏
                            tables.remove(found_table)
                            close_room(create)
                        lock.set()
            else:
                emit('_error', {'msg': '游戏不存在!'}, broadcast=False)
    except KeyError:
        pass


@check_data
@socket_io.on('send_msg')
def send_msg(data):
    try:
        create = session['room']
        secret = session['secret']
        found_table = find_table(create)
        if found_table:
            p = is_player(found_table, secret)
            nick = '观众' if not p else p['nick']
            emit('msg_update', {'nick': nick, 'msg': data.get('msg', 'unknown msg')}, to=create)
    except KeyError:
        pass


def player_leave(create, secret):
    found_table = find_table(create)
    if found_table and secret:
        if is_player(found_table, secret):
            # 玩家离开房间
            if lock.wait(10):
                lock.clear()
                tables.remove(found_table)
                lock.set()
            emit('game_end', {'type': 0}, to=create)
            close_room(create)
        else:
            # 观众离开房间
            try:
                found_table['watch'].remove(secret)
                emit('watcher_num_change', {'num': len(found_table['watch'])}, to=create)
            except ValueError:
                pass
        session['room'] = None
        session['secret'] = None
