from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class TransferRequest(models.Model):
    user = models.ForeignKey(User, related_name='transfer_requests', on_delete=models.CASCADE)
    multisig_address = models.ForeignKey('custody.MultiSigAddress', related_name='transfer_requests', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=32, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        I can't move this into the `clean` method because on object creation,
        I never have raw access to the instance due to how ModelForm works. 
        As a result, `clean` always fails because `self.user` is never set in
        the form.
        """
        if not self.user.is_superuser:
            raise ValidationError({
                'user': ValidationError(_('This user can\'t create transfer requests.'), code='insufficient_permissions'),
            })
        super().save(*args ,**kwargs)

class TransferRequestSignature(models.Model):
    user = models.ForeignKey(User, related_name='transfer_request_signatures', on_delete=models.DO_NOTHING)
    transfer_request = models.ForeignKey(TransferRequest, related_name='signatures', on_delete=models.DO_NOTHING)
    user_agent = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50)
    transaction_body = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
