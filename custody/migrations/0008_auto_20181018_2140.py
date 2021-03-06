# Generated by Django 2.1.2 on 2018-10-18 21:40

from django.db import migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0007_auto_20181018_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multisigaddress',
            name='user_addresses',
            field=smart_selects.db_fields.ChainedManyToManyField(chained_field='currency', chained_model_field='currency', horizontal=True, to='custody.UserAddress'),
        ),
    ]
