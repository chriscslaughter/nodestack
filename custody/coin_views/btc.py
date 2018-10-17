from rest_framework import status
from rest_framework.response import Response

from custody.coin_views import BaseCoin
from custody.models import Currency
from lib.rpc import RPC
from lib.timetools import utc_now, datetime_from_utc_timestamp

class BTCCustody(BaseCoin):
    def __init__(self, coin):
        assert coin in ['BTC', 'LTC', 'BCC']
        self.cur = Currency.objects.get(symbol=coin)

    def status_get(self, request):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        # general status
        blockchaininfo = rpc.make_call("getblockchaininfo", [])
        latest_hash = rpc.make_call("getblockhash", [blockchaininfo["blocks"]])
        latest_block = rpc.make_call("getblock", [latest_hash])
        latest_time = latest_block["time"]
        fee_rate = rpc.make_call("estimatesmartfee", [self.cur.required_confirmations])["feerate"] * 240 / 1024
        status_info = {
            'blocks': blockchaininfo['blocks'],
            'latest_block_time': latest_time,
            'latest_block_age': (utc_now() - datetime_from_utc_timestamp(latest_time)).total_seconds(),
            'fee_rate': fee_rate
        }
        # balance
        balance = {}
        balance["deposits"], balance["withdrawals"], balance["cold_storage"] = {}, {}, {}
        balance["deposits"]["quantity"] = rpc.make_call("getbalance", ["deposits", self.cur.required_confirmations])
        balance["deposits"]["value"] = balance["deposits"]["quantity"] * self.cur.price()
        balance["withdrawals"]["quantity"] = rpc.make_call("getbalance", ["withdrawals", self.cur.required_confirmations])
        balance["withdrawals"]["value"] = balance["withdrawals"]["quantity"] * self.cur.price()
        balance["cold_storage"]["quantity"] = rpc.make_call("getbalance", [self.cur.cold_storage_address, self.cur.required_confirmations, True])
        balance["cold_storage"]["value"] = balance["cold_storage"]["quantity"] * self.cur.price()
        status_info.update({"balance": balance})
        return Response(status_info, status=status.HTTP_200_OK)

    def depositsaddress_post(self, request):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        address = rpc.make_call("getnewaddress", ["deposits"])
        address_info = {
            "address": address,
            "created_at": utc_now().timestamp()
        }
        return Response(address_info, status=status.HTTP_201_CREATED)
#

    def deposits_get(self, request, coin, format=None):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        block = int(request.GET.get('block', 0))
        block_hash = rpc.make_call("getblockhash", [block])
        transactions_ = rpc.make_call("listsinceblock", [block_hash, self.cur.required_confirmations])
        block_height = rpc.make_call("getblock", [transactions_["lastblock"]])["height"]
        result = {
            "lastblock": block_height,
            "transactions": [{
                "address": transaction["address"],
                "amount": transaction["amount"],
                "confirmations": transaction["confirmations"],
                "txid": transaction["txid"],
                "time": transaction["timereceived"]
            } for transaction in transactions_["transactions"] if transaction["account"] == "deposits" and transaction["amount"] >= 0]
        }
        return Response(result, status=status.HTTP_200_OK)

    def depositscoldstoragetransfer_post(self, request, coin, format=None):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        deposits_balance = rpc.make_call("getbalance", ["deposits", self.cur.required_confirmations])
        result = {
            "starting_balance": deposits_balance
        }
        if deposits_balance > 0:
            txid = rpc.make_call("sendfrom", ["deposits", self.cur.cold_storage_address, deposits_balance, self.cur.required_confirmations])
            result = {
                "txid": txid,
                "created_at": utc_now().timestamp()
            }
            return Response(result, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)

    def withdrawalsaddress_post(self, request, coin, format=None):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        address = rpc.make_call("getnewaddress", ["withdrawals"])
        address_info = {
            "address": address,
            "created_at": utc_now().timestamp()
        }
        return Response(address_info, status=status.HTTP_201_CREATED)

    def withdrawals_get(self, request, coin, format=None):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        block = int(request.GET.get('block', 0))
        block_hash = rpc.make_call("getblockhash", [block])
        transactions_ = rpc.make_call("listsinceblock", [block_hash, self.cur.required_confirmations])
        block_height = rpc.make_call("getblock", [transactions_["lastblock"]])["height"]
        result = {
            "lastblock": block_height,
            "transactions": [{
                "address": transaction["address"],
                "amount": -transaction["amount"],
                "confirmations": transaction["confirmations"],
                "txid": transaction["txid"],
                "time": transaction["timereceived"]
            } for transaction in transactions_["transactions"] if transaction["account"] == "withdrawals" and transaction["amount"] < 0]
        }
        return Response(result, status=status.HTTP_200_OK)

    def withdrawalswithdrawal_post(self, request, coin, format=None):
        rpc = RPC(self.cur.node.ip_address, self.cur.node.user, self.cur.node.password)
        # check input
        if "address" not in request.data.keys() or "amount" not in request.data.keys():
            return Response({"msg": "Must specify address and amount."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = float(request.data["amount"])
            assert amount > 0
        except:
            return Response({"msg": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
        address = request.data["address"]
        if not rpc.make_call("validateaddress", [address])["isvalid"]:
            return Response({"msg": "Invalid address."}, status=status.HTTP_400_BAD_REQUEST)
        # check sufficient funds
        balance = rpc.make_call("getbalance", ["withdrawals", self.cur.required_confirmations])
        if balance <= amount:
            return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)
        # initiate withdrawal
        txid = rpc.make_call("sendfrom", ["withdrawals", address, str(amount), self.cur.required_confirmations])
        result = {
            "txid": txid,
            "created_at": utc_now().timestamp()
        }
        return Response(result, status=status.HTTP_202_ACCEPTED)

    def depositscoldstoragetransfer_post(self, request, coin, format=None):
        pass
