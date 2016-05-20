u"""
Player daemon that handles asynchronous playback.
"""
from __future__ import with_statement
from __future__ import absolute_import
import sys
import os
import time
import atexit
import signal
import subprocess
import pafy
from .process import kill_process_tree

# Temporary change logging level until a bug with pafy is fixed to suppress
# unnecessary error
import logging
from io import open
logging.getLogger().setLevel(logging.ERROR)

class Player(object):

    u"""Daemon that controls the music player. Based on implementation by anon at
    http://jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/#c35
    """

    def __init__(self, pidfile, url, show_video=False, verbose=False):
        self.pidfile = pidfile
        self.url = url
        self.show_video = show_video
        self.verbose = verbose


    def print_info(self):
        u"""Prints video information and usage output to stdout"""

        video_data = pafy.new(self.url)
        print u"Now playing: " + video_data.title + u" [" + video_data.duration + u"]"

        # Handle passed-in options
        if self.verbose:
            print u"URL: " + self.url
            print u"Description: " + video_data.description
        if self.show_video:
            print u"Showing video in an external window."

    def daemonize(self):
        u"""Daemonize class. UNIX double fork mechanism."""

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)

        except OSError, err:
            sys.stderr.write(u'fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir(u'/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError, err:
            sys.stderr.write(u'fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()      #
        sys.stderr.flush()
        si = open(os.devnull, u'r')
        so = open(os.devnull, u'a+')
        se = open(os.devnull, u'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = unicode(os.getpid())
        with open(self.pidfile, u'w+') as f:
            f.write(pid + u'\n')

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        try:
            with open(self.pidfile, u'r') as f:
                pid = int(f.read().strip())

        except IOError:
            pid = None

        if pid:
            print u"Stopping current song.."
            kill_process_tree(pid)
            self.delpid()

        self.print_info()

        self.daemonize()
        self.run()

    def stop(self):
        u"""Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile, u'r') as pf:
                pid = int(pf.read().strip())

        except IOError:
            pid = None

        if not pid:
            message = u"pidfile {0} does not exist. " + \
                      u"Daemon not running?\n"
        sys.stderr.write(message.format(self.pidfile))
        return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)

        except OSError, err:
            e = unicode(err.args)
            if e.find(u"No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print unicode(err.args)
                    sys.exit(1)

    def restart(self):
        u"""Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        subprocess_args = [u'mpv', self.url, u"--really-quiet"]
        if self.show_video:
            subprocess_args.append(u"--fs")
        else:
            subprocess_args.append(u"--no-video")
        try:
            subprocess.call(subprocess_args)
        except OSError as e:
            if e.errno == 2:
                print("mpv cannot be found.")
                sys.exit(1)
