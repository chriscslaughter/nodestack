from django import forms
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from coldstoragetransfers.models import TransferRequest, TransferRequestSignature
from coldstoragetransfers.helpers.btc import BTCHelper

class TransferRequestForm(forms.ModelForm):
    class Meta:
        model = TransferRequest
        fields = ('multisig_address', 'amount')

    def clean(self):
        btc = BTCHelper()
        if not self.instance.pk:
            try:
                self.instance.raw_transaction_body = btc.create_raw_transaction(self.cleaned_data['amount'], self.cleaned_data['multisig_address'].address)
            except ValueError as e:
                raise ValidationError({'amount': _('The cold storage balance is less than the withdrawal amount.')})

class TransferRequestSignatureForm(forms.ModelForm):
    transaction_body = forms.CharField()
    class Meta:
        model = TransferRequestSignature
        fields = ('transaction_body',)
