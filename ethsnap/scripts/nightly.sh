#!/bin/bash
# nighly.sh
# 
# This script handles the nightly archiving and cleanup for ethsnap.  

[ -z $ETHSNAP_KEEP_ARCHIVES ] ETHSNAP_KEEP_ARCHIVES=1
[ -z $ETHSNAP_ARCHIVE_DIR ] ETHSNAP_ARCHIVE_DIR="/data/archives/main"
[ -z $ETHSNAP_PYTHON ] ETHSNAP_PYTHON="/var/venvs/ethsnap/bin/python"
[ -z $ETHSNAP_ROOT ] ETHSNAP_ROOT="/var/www/ethsnap"

echo "Stopping geth"
systemctl stop geth

echo "Creating snapshot of blockchain"
nice -n 1 $ETHSNAP_PYTHON $ETHSNAP_ROOT/ethsnap/scripts/ethsnap-snapshot.py
echo "Finished creating snapshot!"

echo "Starting geth"
systemctl start geth

echo "Cleaning"
$ETHSNAP_PYTHON $ETHSNAP_ROOT/ethsnap/scripts/ethsnap-cleanup.py -k $ETHSNAP_KEEP_ARCHIVES -a $ETHSNAP_ARCHIVE_DIR

echo "Complete!"