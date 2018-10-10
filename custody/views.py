from rest_framework import views, permissions, status
from rest_framework.response import Response

from django.http import JsonResponse
from .models import Currency
from lib.rpc import RPC, RPCException
from lib.timetools import utc_now, datetime_from_utc_timestamp

def check_coin(func):
    def wrapper(*args, **kwargs):
        if kwargs['coin'] not in [cur.symbol for cur in Currency.objects.all()]:
            return Response({'error': f"Symbol {kwargs['coin']} not supported on this Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        cur = Currency.objects.get(symbol=kwargs['coin'])
        if not hasattr(cur, "node"):
            return Response({'error': f"Symbol {kwargs['coin']} does not have a node on the Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        return func(*args, **kwargs)
    return wrapper

class Status(views.APIView):
    """
    Get the status of the specific node.
    """
    @check_coin
    def get(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            # general status
            blockchaininfo = rpc.make_call("getblockchaininfo", [])
            latest_hash = rpc.make_call("getblockhash", [blockchaininfo["blocks"]])
            latest_block = rpc.make_call("getblock", [latest_hash])
            latest_time = latest_block["time"]
            fee_rate = rpc.make_call("estimatesmartfee", [cur.required_confirmations])["feerate"] * 240 / 1024
            status_info = {
                'blocks': blockchaininfo['blocks'],
                'latest_block_time': latest_time,
                'latest_block_age': (utc_now() - datetime_from_utc_timestamp(latest_time)).total_seconds(),
                'fee_rate': fee_rate
            }
            # balance
            balance = {}
            balance["deposits"] = rpc.make_call("getbalance", ["deposits", cur.required_confirmations])
            balance["withdrawals"] = rpc.make_call("getbalance", ["withdrawals", cur.required_confirmations])
            balance["cold_storage"] = rpc.make_call("getbalance", [cur.cold_storage_address, cur.required_confirmations, True])
            status_info.update({"balance": balance})
            return Response(status_info, status=status.HTTP_200_OK)

class DepositsAddress(views.APIView):
    """
    Get a new deposit address.
    """
    @check_coin
    def post(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            address = rpc.make_call("getnewaddress", ["deposits"])
            address_info = {
                "address": address,
                "created_at": utc_now().timestamp()
            }
            return Response(address_info, status=status.HTTP_201_CREATED)

class Deposits(views.APIView):
    """
    List all deposits [since block number].
    """
    @check_coin
    def get(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            if "block" not in request.GET:
                block = 0
            else:
                block = int(request.GET["block"])
            block_hash = rpc.make_call("getblockhash", [block])
            transactions_ = rpc.make_call("listsinceblock", [block_hash, cur.required_confirmations])
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

class DepositsColdStorageTransfer(views.APIView):
    """
    List all deposits [since block number].
    """
    @check_coin
    def post(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            deposits_balance = rpc.make_call("getbalance", ["deposits", cur.required_confirmations])
            result = {
                "starting_balance": deposits_balance
            }
            if deposits_balance > 0:
                txid = rpc.make_call("sendfrom", ["deposits", cur.cold_storage_address, deposits_balance, cur.required_confirmations])
                result = {
                    "txid": txid,
                    "created_at": utc_now().timestamp()
                }
                return Response(result, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)

class WithdrawalsAddress(views.APIView):
    """
    Get a new deposit address.
    """
    @check_coin
    def post(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            address = rpc.make_call("getnewaddress", ["withdrawals"])
            address_info = {
                "address": address,
                "created_at": utc_now().timestamp()
            }
            return Response(address_info, status=status.HTTP_201_CREATED)

class Withdrawals(views.APIView):
    """
    List all withdrawals [since block number].
    """
    @check_coin
    def get(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            if "block" not in request.GET:
                block = 0
            else:
                block = int(request.GET["block"])
            block_hash = rpc.make_call("getblockhash", [block])
            transactions_ = rpc.make_call("listsinceblock", [block_hash, cur.required_confirmations])
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

class WithdrawalsWithdrawal(views.APIView):
    """
    Initiate a withdrawal to address.
    """
    @check_coin
    def post(self, request, coin, format=None):
        cur = Currency.objects.get(symbol=coin)
        if coin in ['BTC', 'LTC', 'BCC']:
            rpc = RPC(cur.node.ip_address, cur.node.user, cur.node.password)
            print(request.data)
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
            balance = rpc.make_call("getbalance", ["withdrawals", cur.required_confirmations])
            if balance <= amount:
                return Response({"msg": "Insufficient funds to transfer."}, status=status.HTTP_428_PRECONDITION_REQUIRED)
            # initiate withdrawal
            txid = rpc.make_call("sendfrom", ["withdrawals", address, str(amount), cur.required_confirmations])
            result = {
                "txid": txid,
                "created_at": utc_now().timestamp()
            }
            return Response(result, status=status.HTTP_202_ACCEPTED)
            
