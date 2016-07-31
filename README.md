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

## Interesting queries

Most popular (# messages) per conversation:

```sql
select count(*) as msg_count, thread.title from message join thread on thread_id=thread.id group by thread_id order by msg_count;
```

Messages per day and author:

```sql
select date(message.pub_time) as pub_date, count(*) from message where thread_id=63 and author_id=22137 group by pub_date order by pub_date;
```

You can generate a list of dates to check for non-presence of a date in a set (say, days you did _not_ receive a message) using this code (thanks, [Stack Overflow](http://stackoverflow.com/questions/2157282/generate-days-from-date-range)!):

```sql
select a.Date 
from (
    select curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY as Date
    from (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as a
    cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as b
    cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as c
) a
where a.Date between '2010-01-20' and '2010-01-24' 
```

This allows us to ask things like "how many days of the month did I not receive a message from person X during the period A-B?:

```sql
select year(a.Date), month(a.Date), count(*) silent_days from            (select curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY as Date                    from (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as a                         cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as b     cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as c ) a where a.Date between '2015-12-18' and '2016-07-30' and a.Date not in (select distinct date(message.pub_time) as pub_date from message where thread_id=63        and author_id=22137) group by month(a.Date),year(a.Date) order by silent_days;
```

Perhaps, it is easier to do this by counting _active_ days in stead:

```sql
select year(day), month(day), count(*) from(select distinct date(pub_time) as day from message where thread_id=1 and author_id=1) as day group by year(day), month(day) order by year(day), month(day);
```
