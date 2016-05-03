#!/usr/bin/env python2
from __future__ import with_statement
from __future__ import absolute_import
import os
import sys
import re
import subprocess

from urllib import urlencode
from io import open
from urlparse import urlparse
from urllib2 import urlopen

import argparse
import pafy
from .player import Player
from .process import kill_process_tree
from .process import toggle_process_tree

USAGE = u"""Usage: amp [SEARCH TERMS]
Pass search terms to YouTube and play the first result in a background process.
Call again with no arguments to stop playback.
"""

def main():
    pidfile = u"/tmp/amp.pid"

    parser = argparse.ArgumentParser(description=u"""Pass search terms to YouTube
    and play the first result in a background process.
    Call again with no arguments to pause or resume playback.""",
                                     prog=u'amp',)

    parser.add_argument(u'-v', action=u'store_true',
                        help=u'show the video as well')

    parser.add_argument(u'-k', action=u'store_true',
                        help=u'kill playback process')

    parser.add_argument(u'--verbose', action=u'store_true',
                        help=u'show verbose output')

    parser.add_argument(u'--version', action=u'version', version=u'%(prog)s 0.1.24-2')

    args = parser.parse_known_args()

    # If amp is called with no search terms, try to pause playback.
    if len(args[1]) == 0:
        try:
            with open(pidfile, u'r') as f:
                # Read the pidfile to get the pid of the process to kill.
                pid = int(f.read().strip())

                # If the -k flag is set, kill the process tree completely.
                if args[0].k:
                    kill_process_tree(pid)
                    os.remove(pidfile)
                    print u'Killed playback process.'
                    return

                # Otherwise, pause or resume the process tree.
                else:
                    try:
                        toggle_process_tree(pid)
                    except:
                        print u'pidfile invalid; was amp killed uncleanly?'

        except:
            # If the pidfile doesn't exist, then playback is not happening.
            # Print the usage message and return.
            parser.print_help()
        sys.exit(0)

    # Process the search terms, taking each argument and forming a string
    if args[1]:
        input = u" ".join(args[1])

    else:
        parser.print_help()
        sys.exit(0)

    query_string = urlencode({u"search_query": input})

    html_content = urlopen(u"https://www.youtube.com/results?" +
                           query_string)

    search_results = re.findall(ur'href=\"\/watch\?v=(.{11})',
                                html_content.read())

    url = u"https://www.youtube.com/watch?v=" + search_results[0]
    player = Player(pidfile, url,
                    show_video=args[0].v, verbose=args[0].verbose)
    player.start()

if __name__ == u'__main__':
    sys.exit(main())
