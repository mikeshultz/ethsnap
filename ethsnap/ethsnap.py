#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, configparser, sqlite3
from datetime import datetime
from flask import Flask, Markup, json, render_template
app = Flask(__name__, template_folder='templates')

#CWD = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read("/etc/ethsnap.ini")
SQLITE_DB = config.get('default', 'sqlite', fallback="/var/ethsnap/ethsnap.db")
FLASK_ADDR = config.get('flask', 'address', fallback="127.0.0.1")
FLASK_PORT = config.getint('flask', 'port', fallback=5000)

def b_to_gb(b):
    """ Convert int of bytes to string of gigbates """
    return "%.2f" % (b / 1024 / 1024 / 1024)

class Snapshots:
    def __init__(self):
        
        self.db = sqlite3.connect(SQLITE_DB)
        self.snapshots = []

    def _get_snapshots(self, limit=3):
        """ Get the latest [limit] snapshots """
        
        cur = self.db.cursor()
        cur.execute("""SELECT timestamp, filename, size, sha1 
                       FROM snapshots 
                       ORDER BY timestamp DESC 
                       LIMIT :limit""", {'limit': limit})
        self.sql_result = cur.fetchall()

    def _generate_list(self):
        """ Generate a list of objects from the sql results """
        
        self.snapshots = []
        for snap in self.sql_result:
            self.snapshots.append({
                'timestamp': datetime.fromtimestamp(snap[0]),
                'file': snap[1],
                'size': b_to_gb(snap[2]),
                'sha1': snap[3],
            })

    def fetch(self, limit=3):
        print("fetch")
        self._get_snapshots(limit)
        self._generate_list()

    def json(self):
        self.fetch()
        return json.dumps(self.snapshots)

    def render(self):
        self.fetch()
        return render_template("file_list.html", **{'files': self.snapshots})

@app.route('/')
def index():
    s = Snapshots()
    s.fetch()
    return render_template("index.html", **{'files': s.snapshots})

@app.route('/json')
def snapsots():
    s = Snapshots()
    return s.json()

if __name__ == "__main__":
    app.run(host=FLASK_ADDR, port=FLASK_PORT)