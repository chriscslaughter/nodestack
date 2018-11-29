from coldstoragetransfers.models import TransferRequest, TransferRequestSignature
from django import forms

class TransferRequestForm(forms.ModelForm):
    class Meta:
        model = TransferRequest
        fields = ('multisig_address', 'amount')

class TransferRequestSignatureForm(forms.ModelForm):
    class Meta:
        model = TransferRequestSignature
        fields = ('transaction_body',)
