# Generated by Django 2.1.2 on 2018-12-05 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0020_auto_20181129_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='multisigaddress',
            name='redeem_script',
            field=models.CharField(default='foo', max_length=1000),
            preserve_default=False,
        ),
    ]
