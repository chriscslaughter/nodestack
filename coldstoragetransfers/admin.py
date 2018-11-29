from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from coldstoragetransfers.models import TransferRequest, TransferRequestSignature

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TransferRequestSignatureInline(admin.TabularInline):
    model = TransferRequestSignature

class TransferRequestAdmin(admin.ModelAdmin):
    inlines = [
        TransferRequestSignatureInline
    ]
    model = TransferRequest
    # exclude = ('user_agent', 'ip_address', 'user')
    readonly_fields = ('user_agent', 'ip_address')

    def get_changeform_initial_data(self, request):
        return {
            'ip_address': get_client_ip(request),
            # 'user_agent': request.META['HTTP_USER_AGENT']
        }

    def user_agent(self, instance):
        return mark_safe("<span class='errors'>I can't determine this address.</span>")

    user_agent.short_description = 'short desc'

admin.site.register(TransferRequest, TransferRequestAdmin)
