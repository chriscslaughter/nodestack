import logging
import json
 
from lib.rpc import RPC, RPCException
from custody.models import Currency

# Get an instance of a logger
logger = logging.getLogger(__name__)

class BTCHelper:
    def __init__(self):
        cur = Currency.objects.get(symbol='BTC')
        self.rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)

    def add_multisig_address(self, sigs_required, public_keys):
        if sigs_required > len(public_keys):
            raise ValueError("you're asking for more signatures than signatories")
        address = self.rpc.make_call('addmultisigaddress', [sigs_required, public_keys])['address']
        return address

    def create_raw_transaction(self):
        pass
