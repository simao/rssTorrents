#!/usr/bin/env python
#
# Python script to parse a RSS feed containing torrent files urls and
# add new torrent files to deluge based on the time of the last added
# torrent. The script stores the RSS item date of the last added
# torrent and adds a new torrent to the BT client if the RSS contains
# one or more items with a later date.
#
# TODO: Implement some type of error handling when errors are returned
# while adding new torrents to transmission and try again
# periodically.
#
# Time-stamp: <17:42:16 Sun 01-05-2011 obelix>
#
import feedparser
import pickle
from datetime import datetime
from datetime import timedelta
import time
import commands
import os.path, sys
import simplejson as json
import logging

LOG_FORMAT = '[%(levelname).1s] [%(asctime)s] [%(name)s] %(message)s'
SCRIPTDIR = os.path.abspath(os.path.dirname(sys.argv[0]))
DATEFILE = os.path.join(SCRIPTDIR, "rsstorrents.pid")
SETTINGSFILE = os.path.join(SCRIPTDIR, "rssTorrentsSettings.json")
TORRENTCOMMAND = "transmission-remote -n transmission:transmission -a "
DEFAULTWEEKS = 1

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
_log = logging.getLogger(__name__)

# Get URL from json settings file
# This way, my pipe remains semi non-public at github
with open(SETTINGSFILE, "rb") as f:
    settings = json.load(f)
    rssFile = settings.get("url")

# Read the date, download shows from last DEFAULTWEEKS weeks if we
# can't read any date
try:
    with open(DATEFILE, "rb") as f:
        lastdate = pickle.load(f)
        _log.info("Read date %s" % lastdate)
except Exception:
    lastdate = datetime.now() - timedelta(weeks=DEFAULTWEEKS)
    _log.info("Could not read date of last feed, using last 3 weeks %s" % lastdate)


# Fetch RSS File
feedInfo = feedparser.parse(rssFile)

# Fetch all items until date is later than the stored date
# Add all files to deluge
n = 0
for entry in feedInfo.entries:
    feedDate = datetime.fromtimestamp(time.mktime(entry.modified_parsed))

    if feedDate > lastdate:
        torrentURL = entry.enclosures[0]['href']
        _log.info("Adding torrent %s" % entry.title)

        outputstatus  = commands.getstatusoutput(TORRENTCOMMAND + torrentURL)
        if(outputstatus[0] != 0):
            "Error adding torrent: %s" % outputstatus[1]
        else:
            n = n + 1            
    else:
        break

if len(feedInfo.entries):
    # Set the last date to the date of the most recent item of the RSS feed
    lastdate = datetime.fromtimestamp(time.mktime(feedInfo.entries[0].modified_parsed))
    try:
        with open(DATEFILE, "wb") as f:
            pickle.dump(lastdate, f)
            _log.info("Saved date %s on pid file at %s" % (lastdate, DATEFILE))
    except Exception:
        _log.exception("Could not save date of last feed")
else:
    _log.info("Not saving last date, supplied feed does not contain any valid entries")

# Feedback user
_log.info("Added %d torrents." % n)
_log.info("Finished")
