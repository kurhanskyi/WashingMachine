
from flask import Flask, render_template, redirect, url_for
import sqlite3
import time

app = Flask(__name__)


def get_db():
    db = sqlite3.connect('washing_machine.db')
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS washing_cycles '
               '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
               'phase TEXT, start_time REAL, duration INTEGER)')
    db.commit()

init_db()

class WashingMachine:
    def __init__(self):
        self.durations = {
            'fill': 6,
            'wash': 60,
            'rinse': 15,
            'spin': 5
        }

    def start_phase(self, phase):
        db = get_db()
        db.execute('INSERT INTO washing_cycles (phase, start_time, duration) '
                   'VALUES (?, ?, ?)', (phase, time.time(), self.durations[phase]))
        db.commit()

    def get_current_phase(self):
        db = get_db()
        row = db.execute('SELECT * FROM washing_cycles '
                         'ORDER BY start_time DESC LIMIT 1').fetchone()
        if row:
            elapsed = time.time() - row['start_time']
            if elapsed < row['duration']:
                return row['phase']
        return None

    def get_remaining_time(self):
        db = get_db()
        row = db.execute('SELECT * FROM washing_cycles '
                         'ORDER BY start_time DESC LIMIT 1').fetchone()
        if row:
            elapsed = time.time() - row['start_time']
            remaining = max(0, row['duration'] - elapsed)
            return int(remaining)
        return 0

washing_machine = WashingMachine()

@app.route('/')
def index():
    phase = washing_machine.get_current_phase()
    remaining_time = washing_machine.get_remaining_time()
    return render_template('index.html'
                           '', phase=phase, remaining_time=remaining_time)

@app.route('/start/<phase>')
def start_phase(phase):
    if phase in washing_machine.durations:
        washing_machine.start_phase(phase)
    return redirect(url_for('index'))

@app.route('/history')
def history():
    db = get_db()
    cycles = db.execute('SELECT * FROM washing_cycles ORDER BY start_time DESC').fetchall()
    return render_template('index.html', cycles=cycles)

if __name__ == '__main__':
    app.run(debug=True, port=1945)