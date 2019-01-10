import logging
from decimal import Decimal

from lib.rpc import RPC
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
        self.rpc.make_call('importaddress', [create_payload['address'], "", False])
        return create_payload

    def create_raw_transaction(self, amount, address):
        unspents = self.rpc.make_call('listunspent', [self.required_confirmations, 999999, [address]])

        total = DEFAULT_ZERO
        raw_inputs = []
        for unspent in unspents:
            total += Decimal(unspent['amount']).quantize(DEFAULT_ZERO)
            basic_input = {'txid': unspent['txid'], 'vout': unspent['vout']}
            raw_inputs.append(basic_input)
            if total >= amount:
                break

        fee = self.generate_fee(len(raw_inputs))
        logger.debug('fee: ' + str(fee))
        full_amount = Decimal(Decimal(amount).quantize(DEFAULT_ZERO) + fee).quantize(DEFAULT_ZERO)
        logger.debug('full amount: ' + str(full_amount))

        balance = self.get_balance(address)
        logger.debug('balance: ' + str(balance))
        if balance < full_amount:
            raise ValueError('the cold storage balance is less than the withdrawal amount')


        total = Decimal(total).quantize(DEFAULT_ZERO)
        logger.debug('total: ' + str(total))

        outputs = {
            self.cur.withdrawal_address: float(amount),
            address: float(Decimal(total - full_amount).quantize(DEFAULT_ZERO))
        }

        logger.debug('raw inputs: ' + str(raw_inputs))
        logger.debug('outputs: ' + str(outputs))
        result = self.rpc.make_call('createrawtransaction', [raw_inputs, outputs])
        return result, fee

    def get_balance(self, address):
        unspents = self.rpc.make_call('listunspent', [self.required_confirmations, 999999, [address]])
        balance = sum([Decimal(unspent['amount']).quantize(DEFAULT_ZERO) for unspent in unspents])
        return balance

    def generate_fee(self, input_count):
        """
        generated equation y = 303.9836x + 23.92763 using linear regression with
        inputs:
        tx inputs       byte size
        1               270
        2               664
        3               960
        4               1252
        5               1552
        6               1848
        9               2741
        """
        result = 303.9836 * input_count + 23.92763
        if input_count < 9:
            result += result * .05
        fee = (self.rpc.make_call('estimatesmartfee', [5])['feerate'] / 1000) * result
        return Decimal(fee).quantize(DEFAULT_ZERO)

    def send_raw_transaction(self, transaction):
        txid = self.rpc.make_call('sendrawtransaction', [transaction])
        return txid
