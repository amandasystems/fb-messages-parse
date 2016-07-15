#!/usr/bin/env python3

# import numpy as np
# import matplotlib.pyplot as plt
import message

import MySQLdb

MESSAGE_FILE = "/home/albin/Downloads/fb-dump-2/html/messages.htm"
# längsta/medel/mediantid mellan kommunikation
# meddelanden per person (respektive)
# meddelanden per datum (inte snitt) + plot

DBCONF = {
    "host":
    "localhost",
    "user": "root",
    "db": "FBMSG",
    "use_unicode": True,
    "charset": "utf8",
}

if __name__ == '__main__':
    msgs = message.parse(MESSAGE_FILE)

    print("Parsing message file...")
    threads = message.parse(MESSAGE_FILE)
    print("Message file parsed, begin database upload.")

    with MySQLdb.connect(**DBCONF) as cursor:
        for thread in threads:
            # Add thread to database:
            cursor.execute(
                u"""
                INSERT IGNORE INTO thread (title)
                VALUES (%s)
                """, [thread.name])

            thread_id = cursor.lastrowid

            if thread_id == 0:
                cursor.execute("""
                select id from thread where \
                title = %s
                """, [thread.name])
                thread_id = cursor.fetchone()[0]
            else:
                print("Created thread with id %s." % thread_id)

            for msg in thread.messages:

                # Add author to database (ignoring duplicates)
                cursor.execute(
                    u"""
                    INSERT IGNORE INTO author (name)
                    VALUES (%s)
                    """, [msg.author_name])

                author_id = cursor.lastrowid

                if author_id == 0:
                    cursor.execute("""
                    select id from author where \
                    name = %s
                    """, [msg.author_name])
                    author_id = cursor.fetchone()[0]
                else:
                    print("Inserted author with id %s." % author_id)

                # Add message to database:
                cursor.execute(
                    u"""
                    INSERT INTO message
                    (msg_text, pub_time, author_id, thread_id)
                    VALUES (%s, %s, %s, %s);
                    """, [msg.msg_text, msg.pub_time, author_id, thread_id])

        # plt.plot(dates, 'ro')
        # plt.savefig('foo.png')
        # plt.show()
