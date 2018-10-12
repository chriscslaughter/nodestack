from django.core.management.base import BaseCommand, CommandError

import bit

SUPPORTED_KEYS = ["BTC"]

class Command(BaseCommand):
    help = 'Generates a secret key!'

    def add_arguments(self, parser):
        parser.add_argument('--coin', type=str)

    def handle(self, *args, **options):
        priv = None
        address = None
        if options['coin'] == "BTC":
        	key = bit.Key()
        	priv = key.to_hex()
        	address = key.address
        print("Generated {} key:".format(options['coin']))
        print("     priv: " + str(priv))
        print("  address: " + str(address))