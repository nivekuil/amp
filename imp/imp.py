#!/usr/bin/env python
import urllib.request, urllib.parse
import os, sys, re, subprocess
from daemonize import Daemonize
from signal import SIGTERM

def play():
    subprocess.call(['mpv', url, "--no-video", "--really-quiet"])

def main():
  # Take each command line argument and join as a string
  input = "".join(sys.argv[1:])

  query_string = urllib.parse.urlencode({"search_query" : input})
  html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
  search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
  url = "http://www.youtube.com/watch?v=" + search_results[0]
  print("Now playing: " + url)

  pid = "/tmp/test.pid"
  daemon = Daemonize(app="imp", pid=pid, action=play)
  daemon.start()

if __name__ == "__main__":
  main()
