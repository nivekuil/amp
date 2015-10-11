#!/usr/bin/env python3
import os
import sys
import re
import subprocess

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen

import argparse
import pafy
from .player import Player
from .process import kill_process_tree
from .process import toggle_process_tree

USAGE = """Usage: amp [SEARCH TERMS]
Pass search terms to YouTube and play the first result in a background process.
Call again with no arguments to stop playback.
"""


def main():
    pidfile = "/tmp/amp.pid"

    parser = argparse.ArgumentParser(description="""Pass search terms to YouTube
    and play the first result in a background process.
    Call again with no arguments to pause or resume playback.""",
                                     prog='amp',)

    parser.add_argument('-v', action='store_true',
                        help='show the video as well')

    parser.add_argument('-k', action='store_true',
                        help='kill playback process')

    parser.add_argument('--verbose', action='store_true',
                        help='show verbose output')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1.8')

    args = parser.parse_known_args()

    # If amp is called with no search terms, try to pause playback.
    if len(args[1]) == 0:
        try:
            with open(pidfile, 'r') as f:
                # Read the pidfile to get the pid of the process to kill.
                pid = int(f.read().strip())

                # If the -k flag is set, kill the process tree completely.
                if args[0].k:
                    kill_process_tree(pid)
                    os.remove(pidfile)
                    print('Killed playback process.')

                # Otherwise, pause or resume the process tree.
                else:
                    toggle_process_tree(pid)

        except:
            # If the pidfile doesn't exist, then playback is not happening.
            # Print the usage message and return.
            parser.print_help()
        sys.exit(0)

    # Process the search terms, taking each argument and forming a string
    if args[1]:
        input = " ".join(args[1])

    else:
        parser.print_help()
        sys.exit(0)

    query_string = urlencode({"search_query": input})

    html_content = urlopen("https://www.youtube.com/results?" +
                                          query_string)

    search_results = re.findall(r'href=\"\/watch\?v=(.{11})',
                                html_content.read().decode())

    url = "https://www.youtube.com/watch?v=" + search_results[0]
    player = Player(pidfile, url,
                    show_video=args[0].v, verbose=args[0].verbose)
    player.start()

if __name__ == '__main__':
    sys.exit(main())
