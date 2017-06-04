#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse
import configparser
import datetime
import tempfile
import sqlite3
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ini", help="The ethsnap ini configuration", \
    metavar="FILE", nargs=1, default="/etc/ethsnap.ini")
args = parser.parse_args()

# open and parse config file
config = configparser.ConfigParser()
config.read(args.ini)

# Store what we need
OUT_DIR = config.get('default', 'archivedir')
DATA_DIR = config.get('default', 'datadir', \
    fallback=os.path.expanduser("~/.ethereum"))
SQLITE_FILE = config.get('default', 'sqlite', fallback="/var/ethsnap/ethsnap.db")
TIMEOUT = config.getint('default', 'timeout', fallback=3600)

# sanity checks
if not os.path.isdir(OUT_DIR):
    print("%s is not a directory" % OUT_DIR, file=sys.stderr)
    sys.exit(1)
if not os.path.isdir(DATA_DIR):
    print("%s is not a directory" % DATA_DIR, file=sys.stderr)
    sys.exit(1)

# function to hash files
def hash_file(filename):
    BLOCKSIZE = 65536
    hashy = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hashy.update(buf)
            buf = f.read(BLOCKSIZE)
    return hashy.hexdigest()

# Set our original directory
orig_pwd = os.getcwd()

# Set the location of the DB, but figure out if it's relative or absolute
if SQLITE_FILE[0] == "/":
    sqlite_db = SQLITE_FILE
else:
    sqlite_db = os.path.join(orig_pwd, SQLITE_FILE)

# Compile the output filename we need
output_filename = datetime.datetime.now().strftime("ethereum-chaindata-%Y-%m-%d-%H%M%S.tar.gz")
output_file = os.path.join(OUT_DIR, output_filename)

# Switch to the chaindata directory
os.chdir(os.path.join(DATA_DIR, "geth/chaindata"))

# Run the archive command
process = subprocess.Popen(['tar', '-czf', output_file, '.'], \
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

out, err = process.communicate(timeout=TIMEOUT)
returncode = process.returncode

# Check its return
if returncode != 0:
    print(err, file=sys.stderr)

print("Archive complete")

# Get info on new file
archive_stat = os.stat(output_file)
archive_size = archive_stat.st_size
sha1sum = hash_file(output_file)

# Connect to sqlite db
conn = sqlite3.connect(sqlite_db)

# get the cursor
cur = conn.cursor()

# Create the table if necessary
cur.execute("""CREATE TABLE IF NOT EXISTS snapshots 
    (id integer primary key, timestamp int, sha1 text, size int, filename text)""")

# insert this new record
cur.execute("""INSERT INTO snapshots (timestamp, sha1, size, filename) 
               VALUES (:stamp, :sha1, :size, :file)""", 
    {
        'stamp': datetime.datetime.utcnow().timestamp(), 
        'sha1': sha1sum, 
        'size': archive_size, 
        'file': output_filename
    }
)
conn.commit()