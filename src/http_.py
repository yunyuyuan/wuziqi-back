from src import app, tables
from flask import jsonify, request
from flask_cors import CORS
from threading import Event
from time import time

lock = Event()
lock.set()
CORS(app)


@app.route('/get_table', methods=['post'])
def get_table():
    return jsonify(tables)


@app.route('/create_table', methods=['post'])
def create():
    result = lock.wait(10)
    if result:
        params = request.get_json()
        lock.clear()
        new_table = {
            'player1': params.get('nick', 'unknown'),
            'player2': None,
            'create': int(time())
        }
        tables.append(new_table)
        lock.set()
        return jsonify(new_table['create'])
    else:
        return jsonify(False)
