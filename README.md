Obelisk Monitor
====================

Daemon to monitor a list of btc addresses against an
obelisk server and notify some web service.

Running:
--------------------
You need to provide a file addresses.txt with an address
to monitor on each line.

Provided is a script 'genaddresses.py' you can use to generate
a list of 10K addresses from an mpk.

Modify the following variables in [config.json](config.json):
 * url: url to post for notifications
 * key_id: key id to use for signing posts

Other optional config options:
 * address_file: file to read for addresses (defaults to *addresses.txt*)
 * command_url: obelisk command url (something like *tcp://85.25.198.97:8081*)
 * block_url: obelisk block url (something like *tcp://85.25.198.97:8083*)

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
* [python-zmqproto](https://github.com/caedesvvv/zmqproto)
* [python-obelisk](https://github.com/darkwallet/python-obelisk)
* [python-ecdsa](https://github.com/warner/python-ecdsa)

--

- unsystem dev
