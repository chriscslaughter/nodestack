from rest_framework import status
from decimal import Decimal
from rest_framework.response import Response

from custody.views import BaseCoin
from custody.models import Currency
from lib.rpc import RPC, RPCException
from lib.timetools import utc_now, datetime_from_utc_timestamp

#using a local cache to prevent repeated saves to the db
REQUIRED_CONFIRMATIONS = {}
DEFAULT_ZERO = Decimal('0.00000000')

class BTCCustody(BaseCoin):
    def __init__(self, coin):
        assert coin in ['BTC', 'LTC', 'BCC']
        self.coin = coin
        self.cur = Currency.objects.get(symbol=coin)
        self.rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)

    def get_status(self, request):
        # general status
        blockchaininfo = self.rpc.make_call("getblockchaininfo", [])
        latest_hash = self.rpc.make_call("getblockhash", [blockchaininfo["blocks"]])
        latest_block = self.rpc.make_call("getblock", [latest_hash])
        latest_time = latest_block["time"]
        fee_rate = self.rpc.make_call("estimatesmartfee", [self.cur.required_confirmations])["feerate"] * 240 / 1024
        status_info = {
            'blocks': blockchaininfo['blocks'],
            'latest_block_time': latest_time,
            'latest_block_age': (utc_now() - datetime_from_utc_timestamp(latest_time)).total_seconds(),
            'fee_rate': fee_rate,
            'required_confirmations': self.cur.required_confirmations
        }

        # balance
        balance = {}
        balance["hot_wallet"], balance['hot_wallet_withdrawals'], balance["cold_storage"] = 0, 0, 0

        balance["hot_wallet"] = self.rpc.make_call('getbalance', ['*', self.cur.required_confirmations])
        #balance["hot_wallet"]["value"] = '${:,.2f}'.format(balance["hot_wallet"]["quantity"] * self.cur.price())

        unspents = self.rpc.make_call('listunspent', [0, 999999, [self.cur.cold_storage_address]])
        balance = sum([Decimal(unspent['amount']).quantize(DEFAULT_ZERO) for unspent in unspents])
        balance['cold_wallet'] = balance
        #balance["cold_storage"]["value"] = '${:,.2f}'.format(balance["cold_storage"]["quantity"] * self.cur.price())
        status_info.update({"balance": balance})
        return Response(status_info, status=status.HTTP_200_OK)

    def list_transactions(self, request):
        block = request.GET.get('block')
        if not block:
            block = self.cur.default_block_height
        block = int(block)
        block_hash = self.rpc.make_call("getblockhash", [block])
        transactions = self.rpc.make_call("listsinceblock", [block_hash])
        block_height = self.rpc.make_call("getblock", [transactions["lastblock"]])["height"]
        result = {
            'lastblock': block_height,
            'transactions': [{
                'address': transaction["address"],
                'amount': transaction["amount"],
                'confirmations': transaction["confirmations"],
                'txid': transaction["txid"],
                'time_received': transaction["timereceived"],
                'action': transaction['category']
            } for transaction in transactions["transactions"]
              if 'category' in transaction and
              transaction['category'] in ('send', 'receive')]
        }
        return Response(result, status=status.HTTP_200_OK)

    def get_deposit_address(self, request):
        address = self.rpc.make_call("getnewaddress")
        address_info = {
            "address": address,
            "created_at": utc_now().timestamp()
        }
        return Response(address_info, status=status.HTTP_201_CREATED)

    def submit_withdrawal(self, request):
        # check input
        if "address" not in request.data.keys() or "amount" not in request.data.keys():
            return Response({"msg": "Must specify address and amount."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(request.data["amount"])
            assert amount > 0
        except:
            return Response({"msg": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
        address = request.data["address"]
        if not self.rpc.make_call("validateaddress", [address])["isvalid"]:
            return Response({"msg": "Invalid address."}, status=status.HTTP_400_BAD_REQUEST)
        # check sufficient funds
        balance = self.rpc.make_call('getbalance', ['*', self.cur.required_confirmations])
        if balance <= amount:
            return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)
        # initiate withdrawal
        txid = self.rpc.make_call("sendtoaddress", [address, amount])
        result = {
            "txid": txid,
            "created_at": utc_now().timestamp()
        }
        return Response(result, status=status.HTTP_202_ACCEPTED)
