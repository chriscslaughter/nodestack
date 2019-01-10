from time import time
import requests

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

FEE = {}


class TransferRequest(models.Model):
    user = models.ForeignKey(User, related_name='transfer_requests', on_delete=models.CASCADE)
    multisig_address = models.ForeignKey('custody.MultiSigAddress', related_name='transfer_requests', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=32, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)
    extra = JSONField(null=True)

    @property
    def fee_usd(self):
        if 'fee' not in self.extra:
            return 0
        this_fee = FEE[self.extra['fee']]
        if self.extra['fee'] in FEE and this_fee['timestamp'] + 300 > int(time()):
            return this_fee['value']
        else:
            listings = requests.get("https://api.coinmarketcap.com/v2/listings/").json()["data"]
            id_ = [listing["id"] for listing in listings if listing["symbol"] == self.symbol][0]
            price = requests.get(f"https://api.coinmarketcap.com/v2/ticker/{id_}/").json()["data"]["quotes"]["USD"]["price"]
            this_fee['value'] = price * self.extra['fee']
            this_fee['timestamp'] = int(time()) + 300

    def __str__(self):
        return self.multisig_address.currency.symbol + '_' + \
               self.multisig_address.address +'_' +  \
               str(self.amount)

class TransferRequestSignature(models.Model):
    user = models.ForeignKey(User, related_name='transfer_request_signatures', on_delete=models.DO_NOTHING)
    transfer_request = models.ForeignKey(TransferRequest, related_name='signatures', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    extra = JSONField(null=True)

    def __str__(self):
        return self.user.username + '_' + str(self.created_at)
