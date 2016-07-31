# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, NavigableString, Tag
import dateparser

import re
from copy import copy
from collections import namedtuple
from zipfile import ZipFile

# Filter out characters whose ord() is outside this interval (exclusive)
# Will kill most emoji and other weird data which will not work with MySQL.
MIN_CHAR_ORD = 31
MAX_CHAR_ORD = 300

Message = namedtuple('Message',
                     ['author_name',
                      'pub_time',
                      'msg_text'])

Thread = namedtuple('thread',
                    ['name',
                     'messages'])

## Format: meddelandetexten är innehållet i första grannen till
## <class=message> nedåt, som ska vara en p-tagg första barnet till
## class=thread är trådnamnet alla andra barn till class=thread ska vara
## message eller p-taggar första barnet till message är en div med klass
## message_header message header innehåller en span (klass user)
## innehållande användarnamn och en span med klass meta innehållande
## tidsstämpel.
# <div class=thread>
#   {thread_name}
#   <div class=message>
#     <div class=message_header>
#       <span class=user>{user name}</span>
#       <span class=user>{time stamp}</span>
#     </div>
#   </div>
#   <p>{message text}</p>
# </div>


class ParseError(Exception):
    pass


def clean_str_copy(txt):
    """Return a whitespace-cleaned copy of txt"""
    text = copy(txt)
    text = "".join(i for i in text if MIN_CHAR_ORD < ord(i) < MAX_CHAR_ORD)

    return (re.sub(r'\s+', ' ', text)
            .strip()
            .encode('utf-8')
            .decode('utf-8', 'ignore'))


def make_message(msg):

    # Look for the message text, it's a <p> tag right after the
    # message. If we find anything else, it means the message body was
    # probably empty. On the way there, we may encounter up to two
    # (empty) NavigableStrings, depending on formatting.
    msg_txt = u""
    for sibling in msg.next_siblings:
        if isinstance(sibling, NavigableString):
            continue
        elif sibling.name == 'p':
            msg_txt = clean_str_copy(sibling.get_text())

            break
        elif isinstance(sibling, Tag):
            # Any other tag encountered
            # error = "Expected p tag! Found \"%s\"" % repr(sibling)
            # print(error)
            break
        else:
            raise ParseError("unexpected tag!")

    header = msg.div
    assert header['class'][0] == 'message_header'

    # Clean up spurious whitespaces and newlines:
    author_name = clean_str_copy(header
                                 .find_all("span", class_="user")[0]
                                 .get_text())

    pub_time_block = header.find_all("span", class_="meta")[0].text
    assert pub_time_block

    try:
        # Weird date format override, skip timezone code
        pub_time = dateparser.parse(pub_time_block[:-7])
    except TypeError:
        pub_time = None
        print("Error decoding published block %s" % str(pub_time_block))

    return Message(author_name=author_name,
                   pub_time=pub_time,
                   msg_text=msg_txt)


def parse(filename):
    with ZipFile(filename, mode='r').open('html/messages.htm', mode='r') as f:
        soup = BeautifulSoup(f, 'lxml')

        threads = soup.find_all("div", class_="thread")

        for thread in threads:
            name = clean_str_copy(thread.contents[0])
            messages = map(make_message,
                           thread.find_all("div", class_="message"))

            yield Thread(name=name,
                         messages=messages)
