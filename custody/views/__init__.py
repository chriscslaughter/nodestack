from abc import ABC, abstractmethod
from rest_framework import views, permissions, status
from rest_framework.response import Response

from django.http import JsonResponse
from custody.models import Currency
from lib.rpc import RPC, RPCException
from lib.timetools import utc_now, datetime_from_utc_timestamp

class BaseCoin(ABC):
    @abstractmethod
    def status_get(self, request):
        pass

    @abstractmethod
    def depositsaddress_post(self):
        pass

    @abstractmethod
    def deposits_get(self):
        pass

    @abstractmethod
    def depositscoldstoragetransfer_post(self):
        pass

    @abstractmethod
    def withdrawalsaddress_post(self):
        pass

    @abstractmethod
    def withdrawals_get(self):
        pass

    @abstractmethod
    def withdrawalswithdrawal_post(self):
        pass

def _resolve_method_name(instance, wrapped_function):
    return instance.__class__.__name__.lower() + "_" + wrapped_function.__name__

def route_request(func):
    """
    This routes requests to the correct coin_views/*.py module depending on the
    coin data requested.
    """
    def wrapper(*args, **kwargs):
        coin = kwargs['coin']
        del kwargs['coin']
        if coin not in [cur.symbol for cur in Currency.objects.all()] or \
           coin not in CUSTODY_MAP:
            return Response({'error': f"Symbol {coin} not supported on this Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        custody_class = CUSTODY_MAP[coin]
        cur = Currency.objects.get(symbol=coin)
        if not hasattr(cur, "node"):
            return Response({'error': f"Symbol {coin} does not have a node on the Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        method_name = _resolve_method_name(args[0], func)
        if not hasattr(custody_class, method_name):
            msg = "`%s` is not a method of class `%s`." \
                % (method_name, custody_class.__name__)
            raise ValueError(msg)
        return getattr(CUSTODY_MAP[coin], method_name)(*args[1:])
    return wrapper

class Status(views.APIView):
    """
    Get the status of the specific node.
    """
    @route_request
    def get(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class DepositsAddress(views.APIView):
    """
    Get a new deposit address.
    """
    @route_request
    def post(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class Deposits(views.APIView):
    """
    List all deposits [since block number].
    """
    @route_request
    def get(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class DepositsColdStorageTransfer(views.APIView):
    """
    List all deposits [since block number].
    """
    @route_request
    def post(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class WithdrawalsAddress(views.APIView):
    """
    Get a new deposit address.
    """
    @route_request
    def post(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class Withdrawals(views.APIView):
    """
    List all withdrawals [since block number].
    """
    @route_request
    def get(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

class WithdrawalsWithdrawal(views.APIView):
    """
    Initiate a withdrawal to address.
    """
    @route_request
    def post(self, request, coin, format=None):
        raise NotImplementedError('This should never be reached')

from custody.views.btc import BTCCustody
from custody.views.eth import ETHCustody

CUSTODY_MAP = {
    'BTC': BTCCustody('BTC'),
    'ETH': ETHCustody(),
}
