Obelisk Monitor
--------------------

Daemon to monitor a list of btc addresses against an
obelisk server and notify some web service.

Running:
--------------------
You need to provide a file addresses.txt with an address
to monitor on each line.

Provided is a script 'genaddresses.py' you can use to generate
a list of 10K addresses from an mpk.

Running main.py will start the monitor.

How it works:
--------------------
A python daemon connects to an obelisk server using two zmq
channels, one for history and another for block notifications.

Will post to a web service signing with gpg to notify
changes so web services can keep accounting.

Dependencies:
----------------

* python-twisted-web
* python-obelisk

--

- unsystem dev
