#!/usr/bin/env python3
import os
import sys

import argparse
import pafy
from .player import Player
from .process import kill_process_tree
from .process import toggle_process_tree
from .util import get_search_results

USAGE = """Usage: amp [SEARCH TERMS]
Pass search terms to YouTube and play the first result in a background process.
Call again with no arguments to stop playback.
"""

PIDFILE = '/tmp/amp.pid'
INFOFILE = '/tmp/amp.info'

def main():

    opts = {}

    parser = argparse.ArgumentParser(description="""Pass search terms to YouTube
    and play the first result in a background process.
    Call again with no arguments to pause or resume playback.""",
                                     prog='amp',)

    parser.add_argument('-v', action='store_true',
                        help='show the video as well')
    parser.add_argument('-i', action='store_true',
                        help='print video info')
    parser.add_argument('-k', action='store_true',
                        help='kill playback process')
    parser.add_argument('--verbose', action='store_true',
                        help='show verbose output')
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.1.24-3')

    args = parser.parse_known_args()

    # Handle show video switch
    opts["vid"] = "auto" if args[0].v else "no"

    # Print the info of what's currently playing
    if (args[0].i):
        try:
            with open(INFOFILE, 'r') as f:
                print(f.read())
        except OSError:
            print('No info found.')

        sys.exit(0)

    # If amp is called with no search terms, try to pause playback.
    if len(args[1]) == 0:
        try:
            with open(PIDFILE, 'r') as f:
                # Read the pidfile to get the pid of the process to kill.
                pid = int(f.read().strip())

                # If the -k flag is set, kill the process tree completely.
                if args[0].k:
                    kill_process_tree(pid)
                    os.remove(PIDFILE)
                    print('Killed playback process.')
                    return

                # Otherwise, pause or resume the process tree.
                else:
                    try:
                        toggle_process_tree(pid)
                    except:
                        print('pidfile invalid; was amp killed uncleanly?')

        except OSError:
            # If the pidfile doesn't exist, then playback is not happening.
            # Print the usage message and return.
            parser.print_help()
        sys.exit(0)

    # Process the search terms, taking each argument and forming a string
    if args[1]:
        input = " ".join(args[1])

    else:
        # If there's nothing to do, print help and exit.
        parser.print_help()
        sys.exit(0)

    search_results = get_search_results(input)
    url = 'https://www.youtube.com/watch?v=' + search_results[0]

    player = Player(url, show_video=args[0].v, verbose=args[0].verbose)
    player.start()

if __name__ == '__main__':
    sys.exit(main())
