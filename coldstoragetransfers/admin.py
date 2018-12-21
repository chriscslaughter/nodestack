from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from coldstoragetransfers.models import TransferRequest, TransferRequestSignature
from coldstoragetransfers.forms import TransferRequestForm, TransferRequestSignatureForm
from coldstoragetransfers.helpers.btc import BTCHelper

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TransferRequestSignatureInline(admin.TabularInline):
    model = TransferRequestSignature
    form = TransferRequestSignatureForm
    ordering = ('-created_at',)
    extra = 1

    def get_fields(self, request, obj):
        fields = self.form.Meta.fields
        if obj:
            fields += ('user', 'ip_address', 'user_agent', 'created_at')
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('user', 'ip_address', 'user_agent', 'created_at')
        return super().get_readonly_fields(request, obj)

class TransferRequestAdmin(admin.ModelAdmin):
    form = TransferRequestForm
    change_form_template = 'coldstoragetransfers/admin/transferrequests/change_form.html'
    list_display = ('__str__', 'id', 'created_at')
    inlines = [
        TransferRequestSignatureInline
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        if not instances:
            return
        if len(instances) > 1:
            raise ValueError('should only add one at a time')

        instance = instances[0]
        instance.user = request.user
        instance.user_agent = request.META['HTTP_USER_AGENT']
        instance.ip_address = get_client_ip(request)

        transfer_request = instances[0].transfer_request
        if transfer_request.signatures.count() + 1 >= transfer_request.multisig_address.minimum_signatures and not transfer_request.txid:
            btc = BTCHelper()
            transfer_request.txid = btc.send_raw_transaction(instance.transaction_body)
            transfer_request.save()

        return super().save_formset(request, form, formset, change)

    def redeem_script(self, obj):
        return obj.multisig_address.redeem_script

    def current_balance(self, obj):
        btc = BTCHelper()
        return btc.get_balance(obj.multisig_address.address)

    def get_fields(self, request, obj):
        fields = self.form.Meta.fields
        if obj:
            fields += ('user', 'raw_transaction_body','ip_address', 'user_agent', 'redeem_script', 'current_balance', 'txid')
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('user', 'ip_address', 'user_agent', 'raw_transaction_body', 'redeem_script', 'current_balance', 'txid')

        return super().get_readonly_fields(request, obj)

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('user', 'ip_address', 'user_agent')

        return super().get_exclude(request, obj)


    def get_changeform_initial_data(self, request):
        return {
            'user_agent': request.META['HTTP_USER_AGENT'],
            'ip_address': get_client_ip(request)
        }

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.user_agent = request.META['HTTP_USER_AGENT']
        obj.ip_address = get_client_ip(request)
        obj.save()

admin.site.register(TransferRequest, TransferRequestAdmin)
