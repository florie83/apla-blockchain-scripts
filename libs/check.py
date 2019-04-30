import unittest
import time
from libs import actions, loger, api


log = loger.create_loger(__name__)

def is_tx_in_block(url, wait, tx, token):
    status = actions.tx_status(url, wait, tx['hash'], token)
    if len(status['blockid']) > 0:
        return int(status['blockid'])
    else:
        msg = 'Transaction not in block. Status: ' + str(status)
        log.error(msg)
        unittest.TestCase.fail(msg)
        return None

