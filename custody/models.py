from django.db import models

CURRENCY_CHOICES = (
	('BTC', 'Bitcoin'),
	('LTC', 'Litecoin'),
	('BCH', 'Bitcoin Cash')
)

class Currency(models.Model):
	symbol = models.CharField(max_length=12, choices=CURRENCY_CHOICES, unique=True)
	required_confirmations = models.PositiveIntegerField(default=3)
	def name(self):
		return dict(CURRENCY_CHOICES)[self.symbol]

class Node(models.Model):
	currency = models.OneToOneField('custody.Currency', related_name='node', on_delete=models.CASCADE)
	ip_address = models.CharField(max_length=64)
	user = models.CharField(max_length=64)
	password = models.CharField(max_length=64)