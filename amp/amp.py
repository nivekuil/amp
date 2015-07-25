#!/usr/bin/env python
import urllib.request, urllib.parse
import os, sys, re, subprocess
from signal import SIGTERM

def main():
  pidfile = "/tmp/imp.pid"

  # Take each command line argument and join as a string
  input = "".join(sys.argv[1:])

  if not input:
    with open(pidfile, 'r') as f:
      pid = int(f.read())
      try:
        os.kill(pid, SIGTERM)
        print("Playback stopped.")
      except:
        print("Usage: blah blah.")
      return

  query_string = urllib.parse.urlencode({"search_query" : input})
  html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
  search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
  url = "http://www.youtube.com/watch?v=" + search_results[0]
  print("Now playing: " + url)

  with open(pidfile, 'w') as f:

    player = subprocess.Popen(['mpv', url, "--no-video", "--really-quiet"])
    print(player.pid, end='', file=f)


if __name__ == "__main__":
  main()
