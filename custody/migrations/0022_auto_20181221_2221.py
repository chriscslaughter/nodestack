# Generated by Django 2.1.2 on 2018-12-21 22:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custody', '0021_multisigaddress_redeem_script'),
    ]

    operations = [
        migrations.RenameField(
            model_name='multisigaddress',
            old_name='user_addresses',
            new_name='user_public_keys',
        ),
        migrations.RenameField(
            model_name='useraddress',
            old_name='address',
            new_name='public_key',
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(choices=[('BTC', 'Bitcoin'), ('LTC', 'Litecoin'), ('BCH', 'Bitcoin Cash'), ('ETH', 'Ethereum')], max_length=12, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='useraddress',
            unique_together={('user', 'currency'), ('public_key', 'currency')},
        ),
    ]