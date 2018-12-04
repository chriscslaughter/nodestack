from django.core.management.base import BaseCommand, CommandError

import bit

SUPPORTED_KEYS = ["BTC"]

class Command(BaseCommand):
    help = 'Generates a secret key!'

    def add_arguments(self, parser):
        parser.add_argument('--coin', type=str)
        parser.add_argument('-test', action='store_true')

    def handle(self, *args, **options):
        priv = None
        address = None
        if options['coin'] == "BTC":
            if options['test']:
                key = bit.PrivateKeyTestnet()
            else:
                key = bit.PrivateKey()
            priv = key.to_wif()
            address = key.address
        label = 'LIVE' if not options['test'] else 'TEST'
        print("Generated {} {} key:".format(label, options['coin']))
        print("     priv(wif format): " + str(priv))
        print("      pub: " + str(key.public_key.hex()))
