####################################################
# Obelisk based monitor daemon for easily linking to web services.
#
# Listens for changes to a list of addresses and notifies a given web service
# with updates containing confirmed and unconfirmed transactions for each of
# them.

import sys
import time
import json

from twisted.internet import reactor

import obelisk
from obelisk.util import to_btc

import cypher

# Address History
class AddressHistory(object):
    def __init__(self, address):
        self.address = address
        self.balance = 0
        self.unconfirmed = 0
        self.history = {}

    def add_output(self, tx_hash, height, value):
        self.history[tx_hash] = [height, value]
        self.balance = self.get_balance()
        self.unconfirmed = self.get_unconfirmed()

    def get_balance(self):
        total = 0
        for height, value in self.history.values():
            if height:
                total += value
        return total

    def get_unconfirmed(self):
        total = 0
        for height, value in self.history.values():
            if not height:
                total += value
        return total

    def __str__(self):
        return "AddressHistory('%s', %s, %s)" % (self.address, self.balance, self.unconfirmed)


##############################################
# Service class

class Monitor(obelisk.ObeliskOfLightClient):
    def __init__(self, *args):
        self.naddresses = 0
        self._addresses = {}
        self.load_config()
        obelisk.ObeliskOfLightClient.__init__(self, self.command_url, self.block_url)
        self.load_addresses(self.file_name)


    ##############################################
    # Configuration

    def load_config(self):
        """Load configuration from config.json"""
        try:
            f = open('config.json')
            config = json.load(f)
            f.close()
        except IOError:
            print "error loading configuration"
            config = {}
        self.key_id = str(config.get('key_id', 'FFFFFFFF'))
        self.url = str(config.get('url', ''))
        self.file_name = str(config.get('address_file', 'addresses.txt'))
        self.command_url = str(config.get('command_url', 'tcp://85.25.198.97:8081'))
        self.block_url = str(config.get('block_url', 'tcp://85.25.198.97:8083'))
        if not self.key_id == 'FFFFFFFF':
            print "using gpg key", cypher.get_fingerprint(self.key_id)

    ##############################################
    # Initial history

    def parse_history(self, ec, history, address):
        """Receive history for an address from the server"""
        self._addresses[address] = AddressHistory(address)
        for row in history:
            o_hash, o_index, o_height, value, s_hash, s_index, s_height = row
            if s_height == 0xffffffff:
                self._addresses[address].add_output(o_hash.encode('hex'), o_height, value)
        if self._addresses[address].balance > 0:
            print address, to_btc(self._addresses[address].balance), self._addresses[address]
            # bootstrap notification in case we missed anything
            self.balance_changed(address, [self._addresses[address].get_balance(), self._addresses[address].get_unconfirmed()])

    ##############################################
    # Loading addresses

    def load_address(self, address):
        """Load history for an address and subscribe afterwards"""
        def _on_history(_ec, _history):
            self.naddresses -= 1
            self.parse_history(_ec, _history, address)
            if self.naddresses == 0:
                self.subscribe_addresses(self.file_name)
            if self.naddresses % 1000 == 0:
                print "loaded", 6-self.naddresses, address
            
        self.naddresses += 1
        self.fetch_history(address, _on_history)

    def load_addresses(self, file_name):
        """Load addresses from file"""
        f = open(file_name, 'r')
        for i, address in enumerate(f.readlines()):
            self.load_address(address.strip())
            if i%1000 == 0:
                print 'loading', i, address
        f.close()

    def subscribe_addresses(self, file_name):
        """subscribe addresses from file"""
        f = open(file_name, 'r')
        for i, address in enumerate(f.readlines()):
            self.subscribe_address(address.strip(), self.on_address_update)
            if i%1000 == 0:
                print 'subscribed', i, address
        f.close()


    ##############################################
    # Receiving address updates

    def on_address_update(self, address_version, address_hash, height, block_hash, raw_tx):
        """Callback for address update, receives transactions relevant to the address."""
        address = obelisk.bitcoin.hash_160_to_bc_address(address_hash, address_version), height
        tx = obelisk.bitcoin.Transaction(raw_tx.encode('hex'))
        for output in tx.outputs:
            if address[0] == output[0]:
                print "update for address", address[0], output[1], height
                if not address[0] in self._addresses:
                    self._addresses[address[0]] = AddressHistory(address[0])
                tx_hash = tx.hash()
                history = self._addresses[address[0]]
                history.add_output(tx_hash, height, output[1])
                print tx_hash, history
                self.balance_changed(address[0], [history.get_balance(), history.get_unconfirmed()])


    ##############################################
    # Post to web service

    def balance_changed(self, address, balances):
        """Notify external service about changes to an address"""
        import urllib
        import urllib2
        if balances == [0, 0]:
           return
        timestamp = time.time()
        print "balance changed", address, balances, timestamp
        args = {'timestamp': timestamp,
                'balance': balances[0],
                'balance2': balances[1],
                'address': address}
        if self.key_id == 'FFFFFFFF':
            print "Configure key_id and url to post to webservice"
            return
        data = json.dumps(args)
        signed = cypher.sign_text(data, self.key_id)
        args = urllib.urlencode({'data': signed})
        req = urllib2.Request(self.url, args) #, {'Content-Type': 'application/json'})
        try:
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
        except urllib2.URLError:
            print "error posting to server!"
        print "sent request"


    ##############################################
    # ZMQ Channel

    def on_raw_block(self, height, hash, header, tx_num, tx_hashes):
        """Raw callback for the block zmq channel"""
        print "* block", height, len(tx_hashes)

    def on_raw_transaction(self, hash, transaction):
        """Raw callback for the transaction zmq channel"""
        tx = obelisk.serialize.deser_tx(transaction)
        outputs = []
        for output in tx.outputs:
            print " -", output, dir(output)
            outputs.append(obelisk.util.format_satoshis(output.value))
        print "* tx", hash.encode('hex'), ", ".join(outputs), dir(tx)
 
if __name__ == '__main__':
    c = Monitor()
    # some popular addresses for testing subscription
    if '--test' in sys.argv:
        print "Loading test addresses"
        c.subscribe_address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", c.on_address_update)
        c.subscribe_address("1dice97ECuByXAvqXpaYzSaQuPVvrtmz6", c.on_address_update)
        c.subscribe_address("1VayNert3x1KzbpzMGt2qdqrAThiRovi8", c.on_address_update)
    reactor.run()

