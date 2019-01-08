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
                self.instance.extra = {}
                self.instance.extra['raw_transaction_body'] = btc.create_raw_transaction(self.cleaned_data['amount'], self.cleaned_data['multisig_address'].address)
            except ValueError:
                raise ValidationError({'amount': _('The cold storage balance is less than the withdrawal amount.')})

class TransferRequestSignatureForm(forms.ModelForm):
    transaction_body = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.extra:
            print(self.instance.extra)
            self.fields['transaction_body'].initial = self.instance.extra['transaction_body']

    class Meta:
        model = TransferRequestSignature
        fields = '__all__'

    def clean(self):
        self.instance.extra = self.instance.extra or {}
        self.instance.extra['transaction_body'] = self.cleaned_data['transaction_body']

        transfer_request = self.cleaned_data['transfer_request']
