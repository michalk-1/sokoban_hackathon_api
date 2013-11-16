# -*- coding: utf-8 -*-
from sqlite3 import dbapi2 as sqlite3
from flask import Flask
from flask import request
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import send_from_directory
import json

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/sokapi.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('SOKAPI_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route('/api/v1/map/<int:map_id>')
def get_map(map_id):
    """Loads map with map_id from maps directory as static files"""
    return send_from_directory('./maps', get_map_name(map_id))


@app.route('/api/v1/result/<int:map_id>.json')
def result_render_json(map_id):
    """ returns pretty json """
    results = json.dumps(get_results(map_id))
    return render_template('json.html', results=results)


@app.route('/api/v1/result/<int:map_id>', methods=['POST', 'GET'])
def result(map_id):
    if request.method == 'POST':
        """
        Requires three parameters to submit a result:
          moves - int
          time - int
          user - str
        """
        moves = request.form.get('moves', None)
        time = request.form.get('time', None)
        user = request.form.get('user', None)
        if moves and time and user:
            db = get_db()
            db.execute(
                'INSERT INTO results (map, user, moves, time) \
                 VALUES (?, ?, ?, ?)',
                [map_id, user, moves, time]
            )
            db.commit()
            return redirect(url_for('result', map_id=map_id))
        else:
            abort(400)
    if request.method == 'GET':
        """Responds with top 10 results in json with keys from 1 to 10"""
        result = get_results(map_id)
        return json.dumps(result)


def get_results(map_id):
    db = get_db()
    cur = db.execute(
        'SELECT moves, time, user \
         FROM results \
         WHERE map={} \
         ORDER BY moves, time'.format(map_id)
    )
    entries = cur.fetchall()
    entries = entries[:10]
    result = dict(
        [(i + 1, dict(entries[i])) for i in range(len(entries))]
    )
    return result


def get_map_name(map_id):
    map_name = str(abs(map_id))
    for i in range(3 - len(str(abs(map_id)))):
        map_name = '0' + map_name
    return map_name + '.obj'

if __name__ == '__main__':
    init_db()
    app.run()
