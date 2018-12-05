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
    class Meta:
        model = TransferRequestSignature
        fields = ('transaction_body',)

    # def clean(self):
    #     transfer_request = self.cleaned_data['transfer_request']
    #     print('COUNT')
    #     print(transfer_request.signatures.count())
    #     print('PK')
    #     print(self.instance.pk)
    #     btc = BTCHelper()
    #     if transfer_request.multisig_address.minimum_signatures == transfer_request.signatures.count() + 1 and not transfer_request.txid and not self.instance.pk:
    #         transfer_request.txid = btc.send_raw_transaction(self.cleaned_data['transaction_body'])
    #         transfer_request.save()
