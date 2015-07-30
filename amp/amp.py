#!/usr/bin/env python
import os
import sys
import re
import subprocess
import urllib.request
import urllib.parse
import argparse
import pafy
from player import Player
from util import kill_process_tree

USAGE = """Usage: amp [SEARCH TERMS]
Pass search terms to YouTube and play the first result in a background process.
Call again with no arguments to stop playback.
"""

def main():
    pidfile = "/tmp/amp.pid"

    parser = argparse.ArgumentParser(description="""Pass search terms to YouTube
    and play the first result in a background process.
    Call again with no arguments to stop playback.""")

    parser.add_argument('-v', action='store_true',
                        help='show the video as well')

    args = parser.parse_known_args()

    # Process the search terms, taking each argument and forming a string
    if args[1]:
        input = " ".join(args[1])

    # If amp is called with no search terms, try to stop playback instead.
    else:
        try:
            with open(pidfile, 'r') as f:
                # Read the pidfile to get the pid of the process to kill.
                pid = int(f.read().strip())
                # If the pidfile did exist, kill the process and all of its
                # children, and then remove the pidfile.
                kill_process_tree(pid)
                os.remove(pidfile)
                print("Playback stopped.")

        except:
            # If the pidfile doesn't exist, then playback is not happening.
            # Print the usage message and return.
            parser.print_help()
        sys.exit(0)


    query_string = urllib.parse.urlencode({"search_query": input})

    html_content = urllib.request.urlopen("http://www.youtube.com/results?" +
                                          query_string)

    search_results = re.findall(r'href=\"\/watch\?v=(.{11})',
                                html_content.read().decode())

    url = "http://www.youtube.com/watch?v=" + search_results[0]
    player = Player(pidfile, url)
    player.start(show_video=args[0].v)

if __name__ == "__main__":
    main()
