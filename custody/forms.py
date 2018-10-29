from .models import MultiSigAddress
from django import forms

class MultiSigAddressForm(forms.ModelForm):
    class Meta:
        model = MultiSigAddress
        exclude = ['address']