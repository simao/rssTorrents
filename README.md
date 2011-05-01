# rssTorrents #

## What is this? ##

A Python script to watch one of my Yahoo Pipes containing URLs of new
torrents that I want to download and add them to Transmission
automatically.

# How to use? #

You can peek into the script to customize it to your needs.

With a standard transmission-cli installation on ubuntu, you need to
created the following settings file, name it rssTorrentsSettings.json
and place it in the same dir as rssTorrents.py.

	{
		"url" : "http://url-for-the-feed"
	}

You can then run the script with "python rssTorrents.py".

I also added this command to crontab, this script runs hourly
downloading new torents if there are any.


