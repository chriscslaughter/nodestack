from rest_framework import status
from rest_framework.response import Response

from custody.views import BaseCoin
from custody.models import Currency
from lib.rpc import RPC, RPCException
from lib.timetools import utc_now, datetime_from_utc_timestamp

class BTCCustody(BaseCoin):
    def __init__(self, coin):
        assert coin in ['BTC', 'LTC', 'BCC']
        self.cur = Currency.objects.get(symbol=coin)
        self.rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)

    def list_transactions(self, request):
        block = request.GET.get('block')
        if not block:
            Response({"message": "`block` must be provided"},
                     status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        block = int(block)
        block_hash = self.rpc.make_call("getblockhash", [block])
        transactions = self.rpc.make_call("listsinceblock", [block_hash, self.cur.required_confirmations])
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
