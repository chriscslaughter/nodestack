from django.contrib import admin

# Register your models here.
from .models import Currency, Node, UserAddress

class NodeInline(admin.TabularInline):
	model = Node
	fk_name = 'currency'

class CurrencyAdmin(admin.ModelAdmin):
	model = Currency
	list_display = ('symbol', 'name')
	inlines = (NodeInline,)

class UserAddressAdmin(admin.ModelAdmin):
	model = UserAddress
	fields = ('currency', 'address')
	list_display = ('currency', 'address')
	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.filter(user=request.user)
	def save_model(self, request, obj, form, change):
		if not obj.pk:
			obj.user = request.user
		super().save_model(request, obj, form, change)

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(UserAddress, UserAddressAdmin)