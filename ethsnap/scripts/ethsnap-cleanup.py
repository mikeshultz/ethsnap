#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, glob, argparse

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--keep", help="How many files to keep", \
    metavar="COUNT", nargs=1, default=3)
parser.add_argument("-a", "--archive-dir", dest="directory", \
    help="Directory containing the archives to keep", metavar="DIR", nargs=1)
parser.add_argument("-q", "--quiet", action="store_true", 
    help="Suppress informational messages")
args = parser.parse_args()

archive_files = glob.glob(os.path.join(args.directory[0], "*.tar.xz"))

file_sizes = {}
for f in archive_files:
    file_sizes[f] = os.stat(f).st_mtime

sorted_files = sorted(file_sizes.items(), key=lambda age: age[1])

delete_count = len(sorted_files) - int(args.keep[0])
for x in range(0, delete_count):
    if not args.quiet:
        print("Deleting %s" % sorted_files[x][0])
    os.remove(sorted_files[x][0])