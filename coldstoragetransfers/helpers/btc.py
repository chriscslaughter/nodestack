import logging
import json
from decimal import Decimal
 
from lib.rpc import RPC, RPCException
from custody.models import Currency

# Get an instance of a logger
logger = logging.getLogger(__name__)

DEFAULT_ZERO = Decimal('0.00000000')

class BTCHelper:
    def __init__(self):
        cur = Currency.objects.get(symbol='BTC')
        self.required_confirmations = cur.required_confirmations
        self.rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)

    def add_multisig_address(self, sigs_required, public_keys):
        if sigs_required > len(public_keys):
            raise ValueError("you're asking for more signatures than signatories")
        create_payload = self.rpc.make_call('createmultisig', [sigs_required, public_keys])
        self.rpc.make_call('importaddress', [create_payload['address']])
        return create_payload

    def get_hot_wallet_address(self):
        return self.rpc.make_call('getnewaddress')

    def create_raw_transaction(self, amount, address):
        fee = self.generate_fee()
        logger.debug('fee: ' + str(fee))
        full_amount = Decimal(Decimal(amount).quantize(DEFAULT_ZERO) + fee).quantize(DEFAULT_ZERO)
        logger.debug('full amount: ' + str(full_amount))


        unspents = self.rpc.make_call('listunspent', [self.required_confirmations, 999999, [address]])
        balance = sum([Decimal(unspent['amount']).quantize(DEFAULT_ZERO) for unspent in unspents])
        if balance < full_amount:
            raise ValueError('the cold storage balance is less than the withdrawal amount')

        unspents = self.rpc.make_call('listunspent', [self.required_confirmations, 999999, [address]])

        total = DEFAULT_ZERO
        raw_inputs = []
        for unspent in unspents:
            total += Decimal(unspent['amount']).quantize(DEFAULT_ZERO)
            basic_input = {'txid': unspent['txid'], 'vout': unspent['vout']}
            raw_inputs.append(basic_input)
            if total >= full_amount:
                break

        total = Decimal(total).quantize(DEFAULT_ZERO)
        logger.debug('total: ' + str(total))

        outputs = {
            self.get_hot_wallet_address(): float(amount),
            address: float(Decimal(total - full_amount).quantize(DEFAULT_ZERO))
        }

        logger.debug('raw inputs: ' + str(raw_inputs))
        logger.debug('outputs: ' + str(outputs))
        result = self.rpc.make_call('createrawtransaction', [raw_inputs, outputs])
        return result

    def generate_fee(self):
        return Decimal(0.001).quantize(DEFAULT_ZERO)

    def send_raw_transaction(self, transaction):
        txid = self.rpc.make_call('sendrawtransaction', [transaction])
        return txid
