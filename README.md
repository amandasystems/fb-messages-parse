# What is this?

This is a small and hackish parser for the Facebook Messenger log dump
from Facebook's
"[Download my Data](https://www.facebook.com/help/131112897028467/)". It
just parses the HTML file using Beautiful Soup and inserts it into a
MySQL database for you to query.

## Known issues

It uses the python library `dateparser` to parse dates. However, it does
not understand the format that my Facebook export produces, so the
current version of the script manually strips the time zone information
from the date string by removing the last 7 characters. That's not ideal.

## Set up the database

Warning! This will delete _all old data_!

```
mysql -u root < fb-msg-db.sql
```

Assuming you have
[`virtualenvwrapper`](http://virtualenvwrapper.readthedocs.io/en/latest/)
installed and set up, you can set up a new development environment with
the following commands:

```
mkvirtualenv -p python3 fb-msg
workon fb-msg
pip install -r requirements.txt
```

Just the `pip install` part will probably work without virtualenv, but
it will clutter your system with packages.
