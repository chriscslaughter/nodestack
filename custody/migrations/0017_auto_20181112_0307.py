# Generated by Django 2.1.2 on 2018-11-12 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0016_currency_transfer_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='required_confirmations',
            field=models.PositiveIntegerField(null=True),
        ),
    ]