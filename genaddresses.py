from obelisk.bitcoin import ElectrumSequence

mpk = "yourmpk"

for idx in xrange(10000):
    seq = ElectrumSequence(mpk)
    print seq.get_address((False, idx))


