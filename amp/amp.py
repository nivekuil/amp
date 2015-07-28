#!/usr/bin/env python
import os
import sys
import re
import subprocess
import urllib.request
import urllib.parse
import pafy
from player import Player
from util import kill_process_tree

USAGE = """Usage: amp [SEARCH TERMS]
Pass search terms to YouTube and play the first result in a background process.
Call again with no arguments to stop playback.
"""


def main():
    pidfile = "/tmp/amp.pid"

    # Take each command line argument and join as a string
    input = "".join(sys.argv[1:])

    # If program is called with no input, then try to stop playback.
    if not input:
        try:
            with open(pidfile, 'r') as f:
                # Read the pidfile to get the pid of the process to kill.
                pid = int(f.read().strip())

        except:
            # If the pidfile doesn't exist, then playback is not happening.
            # Print the usage message and return.
            print(USAGE)
            return

        # If the pidfile did exist, kill the process and all of its children
        # processes, and then remove the pidfile.
        kill_process_tree(pid)
        os.remove(pidfile)
        print("Playback stopped.")

        return

    query_string = urllib.parse.urlencode({"search_query": input})

    html_content = urllib.request.urlopen("http://www.youtube.com/results?" +
                                          query_string)

    search_results = re.findall(r'href=\"\/watch\?v=(.{11})',
                                html_content.read().decode())

    url = "http://www.youtube.com/watch?v=" + search_results[0]
    video_data = pafy.new(url)
    player = Player(pidfile, url)
    print("Now playing: " + video_data.title + " (" + video_data.duration + ")")
    player.start()

if __name__ == "__main__":
    main()
