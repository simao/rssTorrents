#!/usr/bin/python2.6
#
# Python script to parse a RSS feed containing torrent files urls and
# add new torrent files to deluge based on the time of the last added
# torrent. The script stores the RSS item date of the last added
# torrent and adds a new torrent to the BT client if the RSS contains
# one or more items with a later date.
#
# Fri Feb 19 01:22:22 WET 2010
#

import feedparser
import pickle
from datetime import datetime
from datetime import timedelta
import time
import commands
import os.path, sys
import json

DATEFILE =  os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "rsstorrents.pid"
SETTINGSFILE = "rssTorrentsSettings.json"
TORRENTCOMMAND = "transmission-remote -n transmission:transmission -a "
DEFAULTWEEKS = 1

# Get URL from json settings file
# This way, my pipe remains semi non-public at github
with open(SETTINGSFILE, "rb") as f:
    settings = json.load(f)
    rssFile = settings.get("url")

# Read the date, download shows from last DEFAULTWEEKS weeks if we can't read any date
try:
    with open(DATEFILE, "rb") as f:
        lastdate = pickle.load(f)
        print "Read date %s" % lastdate
except Exception:
    lastdate = datetime.now() - timedelta(weeks=DEFAULTWEEKS)
    print "Could not read date of last feed, using last 3 weeks %s" % lastdate


# Fetch RSS File
feedInfo = feedparser.parse(rssFile)

# Fetch all items until date is later than the stored date
# Add all files to deluge
n = 0
for entry in feedInfo.entries:
    feedDate = datetime.fromtimestamp(time.mktime(entry.modified_parsed))

    if feedDate > lastdate:
        torrentURL = entry.enclosures[0]['href']
        print "Adding torrent %s" % entry.title

        outputstatus  = commands.getstatusoutput(TORRENTCOMMAND + torrentURL)
        if(outputstatus[0] != 0):
            print "Error adding torrent: %s" % outputstatus[1]
        else:
            n = n + 1            
    else:
        break

# Set the last date to the date of the most recent item of the RSS feed
lastdate = datetime.fromtimestamp(time.mktime(feedInfo.entries[0].modified_parsed))

try:
    with open(DATEFILE, "wb") as f:
        pickle.dump(lastdate, f)
        print "Saved date %s on pid file at %s" % (lastdate, DATEFILE)
except Exception:
    print "Could not save date of last feed"

# Feedback user
print "Added %d torrents." % n
print "Finished at %s.\n" % datetime.today()

