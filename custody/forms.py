import logging

from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext as _

from custody.models import MultiSigAddress
from coldstoragetransfers.helpers.btc import BTCHelper

class MultiSigAddressForm(forms.ModelForm):
    class Meta:
        model = MultiSigAddress
        exclude = ['address']

    def clean(self):
        #{'currency': <Currency: ETH>, 'user_addresses': <QuerySet [<UserAddress: BTC_tipu>, <UserAddress: ETH_tipu>]>, 'minimum_signatures': 2}
        this_currency = self.cleaned_data['currency'].symbol
        errors = {}

        for a in self.cleaned_data['user_addresses']:
            if a.currency.symbol != this_currency:
                errors['user_addresses'] = _("Child addresses' currency must match selected currency.")

        if self.cleaned_data['minimum_signatures'] > len(self.cleaned_data['user_addresses']):
            errors['minimum_signatures'] = _("This amount can't be less than the number of child addresses.")

        if errors:
            raise ValidationError(errors)

        super().clean()

        """
        doesn't work on save_model in the MultisigAddressAdmin due to:
        <MultiSigAddress: BTC_None>" needs to have a value for field "id" before this many-to-many relationship can be used.
        because new models don't exist in the db, relationship can't be accessed. must happen here.
        """

        raw_public_keys = [ua.address for ua in self.cleaned_data['user_addresses']]

        # predictable ordering is required for multisig creation
        raw_public_keys.sort()

        #should only happen once !
        if not self.instance.pk:
            self.instance.address = BTCHelper().add_multisig_address(self.cleaned_data['minimum_signatures'], raw_public_keys)
