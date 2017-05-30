# ethsnap

ethsnap provides nightly ethereum blockchain snapshots.  This is the source code
for [ethsnap.com](https://www.ethsnap.com).

## Deploy

For now, anyway, the best way to deploy this is to just drop it in `/var/www`. 
There may be deploy/install scripts later on, but so far it hasn't made sense.

### Configuration

You should create an ini file for configuration.  This config file path should 
be set in your uwsgi ini file as `pyargv` so ethsnap knows where to find it.

    [default]
    ; How many archives to keep around
    keep = 1
    ; The timeout for the archive script(below is 3 hours)
    timeout = 10800
    ; The location archives should be stored in
    archivedir = /data/archives/main
    ; The ethereum data directory
    datadir = /home/[user]/.ethereum
    ; Where we should put our SQLite DB
    sqlite = /var/ethsnap/ethsnap.db

### virtualenv

This step isn't all that useful for 'ethsnap'.  There aren't a whole lot of 
dependencies.  Though keep in mind this has only been tested on python>=3.4.

    python34 -m venv /var/venvs/ethsnap

### uwsgi

#### Configuration

Your uwsgi should look something like the following: 

    [uwsgi]
    socket = 127.0.0.1:8000
    stats = 127.0.0.1:8001

    logto = /var/log/uwsgi/%n.log

    uid = nginx
    gid = nginx

    binary-path = /var/venvs/ethsnap/bin/uwsgi
    virtualenv = /var/venvs/ethsnap
    chdir = /var/www/ethsnap/ethsnap
    module = ethsnap
    callable = app
    pyargv = /etc/ethsnap.ini

Take note of pyargv.  `ethsnap` expects the first argument to be to the ini file
with its configuration.

### nginx

Basic nginx config should look like this.  I do recommend adding HTTPS config if 
you can.

    server {
            listen 80;
            listen [::]:80;
            server_name example.com www.example.com;

            root /var/www/ethmsg;

            location / {
                    include uwsgi_params;
                    uwsgi_pass 127.0.0.1:8000;
            }

            location /archives {
                    root /data/archives;
            }

    }

### Startup

You should be able to startup uwsgi and nginx and have a workig app.  You might
want to also setup uwsgi using `supervisord`, but that's out of scope for this
document.

## Cron

There are some tasks that need to be done nighly.  The blockchain needs to be 
archived and old archives need to be cleaned up and proper database entries are
to be made.  The entire operation is controlled by `nightly.sh` which runs the 
necessary snapshot and cleanup scripts and handles shutting down of a geth 
service.  

If you aren't using systemd, you may want to skip `nightly.sh` entirely and 
create your own.

If you do use nightly, there's also four environmental variables that you might
need to define, depending on your system.  It's likely the defaults do not fit
with whatever setup you have.

 - `ETHSNAP_KEEP_ARCHIVES` - This tells ethsnap how many archives to keep around.
    The interface only shows the last archive, currently, so it probably makes 
    sense to leave this at 1.
 - `ETHSNAP_ARCHIVE_DIR` - The directory you want the archives stored in.  
    Default is `/data/archives/main`.
 - `ETHSNAP_PYTHON` - The python executable you want to be used for the ethsnap
    scripts.  If you're not using the system default `python`, you probably want
    to define this.  It's also useful if using virualenvs.
 - `ETHSNAP_ROOT` - The root directory for ethsnap.  Defaults to 
    `/var/www/ethsnap`

The best way to go about having this run is a simple cronjob.  For instance, if
you wanted to have this run every evening at midnight: 

    0 0 * * *       /var/www/ethsnap/ethsnap/scripts/nightly.sh > /dev/null 2>&1

Depending on your system resources, this process could take hours.