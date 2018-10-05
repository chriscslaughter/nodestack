from django.contrib import admin

# Register your models here.
from .models import Currency, Node

class CurrencyAdmin(admin.ModelAdmin):
  model = Currency
  list_display = ('symbol', 'name')

admin.site.register(Currency, CurrencyAdmin)