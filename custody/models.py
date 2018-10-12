from django.db import models

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

class Node(models.Model):
	currency = models.OneToOneField('custody.Currency', related_name='node', on_delete=models.CASCADE)
	ip_address = models.CharField(max_length=64)
	user = models.CharField(max_length=64)
	password = models.CharField(max_length=64)