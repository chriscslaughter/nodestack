from django.db import models
from django.conf import settings

CURRENCY_CHOICES = (
	('BTC', 'Bitcoin'),
	('LTC', 'Litecoin'),
	('BCH', 'Bitcoin Cash')
)
CURRENCY_prices = {}
class Currency(models.Model):
	symbol = models.CharField(max_length=12, choices=CURRENCY_CHOICES, unique=True)
	required_confirmations = models.PositiveIntegerField(default=3)
	cold_storage_address = models.CharField(max_length=256, null=True)
	def name(self):
		return dict(CURRENCY_CHOICES)[self.symbol]
	def price(self):
		from lib.timetools import utc_now
		import requests
		if self.symbol not in CURRENCY_prices.keys() or (utc_now() - CURRENCY_prices[self.symbol]["time"]).total_seconds() > 60:
			listings = requests.get("https://api.coinmarketcap.com/v2/listings/").json()["data"]
			id_ = [listing["id"] for listing in listings if listing["symbol"] == self.symbol][0]
			price = requests.get(f"https://api.coinmarketcap.com/v2/ticker/{id_}/").json()["data"]["quotes"]["USD"]["price"]
			CURRENCY_prices[self.symbol] = {
				"time": utc_now(),
				"price": price
			}
		return CURRENCY_prices[self.symbol]["price"]
	def __str__(self):
		return str(self.symbol)

class Node(models.Model):
	currency = models.OneToOneField('custody.Currency', related_name='node', on_delete=models.CASCADE, null=True)
	ip_address = models.CharField(max_length=64)
	user = models.CharField(max_length=64)
	password = models.CharField(max_length=64)

class UserAddress(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, related_name='user_addresses', on_delete=models.CASCADE)
	address = models.CharField(max_length=256, help_text="This is the public address associated with your key. Do NOT input your private key here under any circumstance!")
	created_at = models.DateTimeField(auto_now_add=True)
	def unique_error_message(self, model_class, unique_check):
		print("Hello world!")
		if model_class == type(self) and unique_check == ('user', 'currency'):
			return f'You already have a user address for {self.currency}. Edit that instead.'
		else:
			return super().unique_error_message(model_class, unique_check)
	class Meta:
		unique_together = (
			("user", "currency"),
		)
