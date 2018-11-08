import datetime
from rest_framework import status
from rest_framework.response import Response
from web3 import HTTPProvider, Web3

from custody.views import BaseCoin
from custody.models import Currency
from lib.timetools import utc_now, datetime_from_utc_timestamp

class ETHCustody(BaseCoin):
    def __init__(self):
        self.cur = Currency.objects.get(symbol='ETH')
        self.w3 = Web3(Web3.HTTPProvider(self.cur.node.ip_address))

        #TODO: set addy
        self.hot_wallet_address = "0x"

    def list_transactions(self, request):
        pass

    def get_deposit_address(self, request):
        pass
