from django.contrib import admin
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.forms import ModelForm

# Register your models here.
from custody.models import Currency, Node, UserAddress, MultiSigAddress
from custody.forms import MultiSigAddressForm

class NodeInline(admin.TabularInline):
    model = Node
    fk_name = 'currency'

class CurrencyAdmin(admin.ModelAdmin):
    model = Currency
    list_display = ('symbol', 'name')
    inlines = (NodeInline,)

class MultiSigAddressAdmin(admin.ModelAdmin):
    model = MultiSigAddress
    form = MultiSigAddressForm

class UserAddressAdmin(admin.ModelAdmin):
    model = UserAddress
    list_display = ('currency', 'public_key')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(MultiSigAddress, MultiSigAddressAdmin)
admin.site.register(UserAddress, UserAddressAdmin)
