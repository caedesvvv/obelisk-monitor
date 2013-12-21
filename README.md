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

Modify the following variables in main.py:
 * url: url to post for notifications
 * key_id: key id to use for signing posts

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
* python-pyme
* python-zmqproto (https://github.com/caedesvvv/zmqproto.git)
* python-obelisk (https://github.com/darkwallet/python-obelisk.git)
* python-ecdsa (https://github.com/warner/python-ecdsa.git)

--

- unsystem dev
