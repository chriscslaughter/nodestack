from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from coldstoragetransfers.models import TransferRequest, TransferRequestSignature
from coldstoragetransfers.forms import TransferRequestForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TransferRequestSignatureInline(admin.TabularInline):
    model = TransferRequestSignature

    def get_changeform_initial_data(self, request):
        return {
            'user_agent': request.META['HTTP_USER_AGENT'],
            'ip_address': get_client_ip(request)
        }

class TransferRequestAdmin(admin.ModelAdmin):
    form = TransferRequestForm
    change_form_template = 'coldstoragetransfers/admin/transferrequests/change_form.html'
    inlines = [
        TransferRequestSignatureInline
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('ip_address', 'user_agent')

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
        #obj.raw_transaction_body = BTCHelper().add_multisig_address(self.cleaned_data['minimum_signatures'], raw_public_keys)
        obj.save()

admin.site.register(TransferRequest, TransferRequestAdmin)
