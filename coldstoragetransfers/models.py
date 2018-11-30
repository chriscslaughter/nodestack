from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class TransferRequest(models.Model):
    user = models.ForeignKey(User, related_name='transfer_requests', on_delete=models.CASCADE)
    multisig_address = models.ForeignKey('custody.MultiSigAddress', related_name='transfer_requests', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    raw_transaction_body = models.CharField(max_length=1000)
    amount = models.DecimalField(max_digits=32, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

class TransferRequestSignature(models.Model):
    user = models.ForeignKey(User, related_name='transfer_request_signatures', on_delete=models.DO_NOTHING)
    transfer_request = models.ForeignKey(TransferRequest, related_name='signatures', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    transaction_body = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
