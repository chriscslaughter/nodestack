from django.contrib import admin

# Register your models here.
from .models import Currency, Node

class NodeInline(admin.TabularInline):
  model = Node
  fk_name = 'currency'

class CurrencyAdmin(admin.ModelAdmin):
  model = Currency
  list_display = ('symbol', 'name')
  inlines = (NodeInline,)

admin.site.register(Currency, CurrencyAdmin)