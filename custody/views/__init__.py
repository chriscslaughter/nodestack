from abc import ABC, abstractmethod
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from custody.models import Currency

class BaseCoin(ABC):
    @abstractmethod
    def get_deposit_address(self, request):
        pass

    @abstractmethod
    def list_transactions(self, request):
        pass

def _resolve_method_name(instance, wrapped_function):
    return wrapped_function.__name__

def route_request(func):
    """
    This routes requests to the correct coin_views/*.py module depending on the
    coin data requested.
    """
    def wrapper(*args, **kwargs):
        custody_map = {
            'BTC': BTCCustody('BTC'),
            'ETH': ETHCustody(),
        }
        coin = kwargs['coin']
        del kwargs['coin']
        if coin not in [cur.symbol for cur in Currency.objects.all()] or \
           coin not in custody_map:
            return Response({'error': f"Symbol {coin} not supported on this Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        custody_class = custody_map[coin]
        cur = Currency.objects.get(symbol=coin)
        if not hasattr(cur, "node"):
            return Response({'error': f"Symbol {coin} does not have a node on the Nodestack."}, status=status.HTTP_404_NOT_FOUND)
        method_name = _resolve_method_name(args[0], func)
        if not hasattr(custody_class, method_name):
            msg = "`%s` is not a method of class `%s`." \
                % (method_name, custody_class.__name__)
            raise ValueError(msg)
        return getattr(custody_map[coin], method_name)(*args)
    return wrapper

@api_view(['GET'])
@route_request
def list_transactions(request, coin):
    raise NotImplementedError('This should never be reached')

@api_view(['POST'])
@route_request
def get_deposit_address(request, coin):
    raise NotImplementedError('This should never be reached')

from custody.views.btc import BTCCustody
from custody.views.eth import ETHCustody
