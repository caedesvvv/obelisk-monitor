import obelisk

from twisted.internet import reactor
from obelisk.util import to_btc

####################################################
# Testing Code

class Monitor(obelisk.ObeliskOfLightClient):
    def __init__(self, *args):
        self.naddresses = 0
        self._addresses = {}
        obelisk.ObeliskOfLightClient.__init__(self, *args)
        self.load_addresses('addresses.txt')

    def print_history(self, ec, history, address):
        total = 0
        for row in history:
            o_hash, o_index, o_height, value, s_hash, s_index, s_height = row
            if s_height == 0xffffffff:
                total += value
        if total > 0:
            print address, to_btc(total)
        self._addresses[address] = total

    def load_address(self, address):
        def _print_history(_ec, _history):
            self.naddresses -= 1
            self.print_history(_ec, _history, address)
            if self.naddresses == 0:
                self.subscribe_addresses(self.file_name)
            if self.naddresses % 1000 == 0:
                print "loaded", 10000-self.naddresses
            
        self.naddresses += 1
        self.fetch_history(address, _print_history)

    def load_addresses(self, file_name):
        self.file_name = file_name
        i = 0
        f = open(file_name, 'r')
        for address in f.readlines():
            i+=1
            self.load_address(address.strip())
            if i%1000 == 0:
                print 'loading',i
        f.close()

    def on_address_update(self, address_version, address_hash, height, block_hash, raw_tx):
        address = obelisk.bitcoin.hash_160_to_bc_address(address_hash, address_version), height
        print "update for address", address[0]
        tx = obelisk.bitcoin.Transaction(raw_tx.encode('hex'))
        print "  inputs", len(tx.inputs), tx.inputs[0]['address']
        for output in tx.outputs:
            print " - output", output
            if address[0] == output[0]:
                print "  output", output[1]


    def subscribe_addresses(self, file_name):
        i = 0
        f = open(file_name, 'r')
        for address in f.readlines():
            i+=1
            self.subscribe_address(address.strip(), self.on_address_update)
            if i%1000 == 0:
                print 'subscribed',i
        f.close()


    def balance_changed(self, address, balances):
        if balances == [0, 0]:
           return
        timestamp = time.time()
        print address, balances, timestamp
        args = {'timestamp': timestamp,
                'balance': balances[0],
                'balance2': balances[1],
                'address': address}
        data = json.dumps(args)
        signed = cypher.sign_text(data, key_id)
        args = urllib.urlencode({'data': signed})
        req = urllib2.Request(url, args) #, {'Content-Type': 'application/json'})
        try:
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
        except urllib2.URLError:
            print "error posting to server!"
        print "sent request"

    def on_raw_block(self, height, hash, header, tx_num, tx_hashes):
        print "* block", height, len(tx_hashes)

    def on_raw_transaction(self, hash, transaction):
        tx = obelisk.serialize.deser_tx(transaction)
        outputs = []
        for output in tx.outputs:
            print " -", output, dir(output)
            outputs.append(obelisk.util.format_satoshis(output.value))
        print "* tx", hash.encode('hex'), ", ".join(outputs), dir(tx)
 
if __name__ == '__main__':
    c = Monitor('tcp://85.25.198.97:8081', 'tcp://85.25.198.97:8083')
    # some popular addresses for testing subscription
    c.subscribe_address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", c.on_address_update)
    c.subscribe_address("1dice97ECuByXAvqXpaYzSaQuPVvrtmz6", c.on_address_update)
    c.subscribe_address("1VayNert3x1KzbpzMGt2qdqrAThiRovi8", c.on_address_update)
    reactor.run()

