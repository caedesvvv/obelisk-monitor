"""
Checking gpg signatures
"""

from pyme import core, constants, errors, pygpgme
from pyme.constants.sig import mode

def sign_text(text, key_uid):
    ciphertext = core.Data()
    plaintext = core.Data(text)
  
    ctx = core.Context()
  
    ctx.set_armor(1)
    #ctx.set_passphrase_cb(_passphrase_callback)
  
    ctx.op_keylist_start(key_uid, 0)
    sigkey = ctx.op_keylist_next()
    # print sigkey.uids[0].uid
  
    ctx.signers_clear()
    ctx.signers_add(sigkey)
  
    ctx.op_sign(plaintext, ciphertext, mode.NORMAL)
  
    ciphertext.seek(0, 0)
    signature = ciphertext.read()
  
    return signature

def get_fingerprint(key_id):
    ctx = core.Context()

    ctx.op_keylist_start(key_id, 0)
    sigkey = ctx.op_keylist_next()

    for subkey in sigkey.subkeys:
        if subkey.can_sign:
            return subkey.fpr

def check_signature(text, fingerprint):
    gpg = core.Context()
    plaintext = core.Data()
    signed = core.Data(text)
    try:
        res = gpg.op_verify(signed, None, plaintext)
    except errors.GPGMEError:
        # incorrect data
        return False
        
    plaintext.seek(0,0)
    result_data = plaintext.read()

    res = gpg.op_verify_result()

    s = res.signatures[0]

    if s.fpr == fingerprint:
        return result_data, s.timestamp
    else:
        print 'invalid fingerprint', s.fpr
        return False


