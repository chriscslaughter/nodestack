# Generated by Django 2.1.2 on 2018-11-12 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0018_remove_currency_required_confirmations'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='required_confirmations',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
