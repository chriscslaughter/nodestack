# Generated by Django 2.1.2 on 2018-10-18 21:50

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0009_auto_20181018_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multisigaddress',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cold_storage_addresses', to='custody.Currency'),
        ),
        migrations.AlterField(
            model_name='multisigaddress',
            name='user_addresses',
            field=smart_selects.db_fields.ChainedManyToManyField(chained_field='currency', chained_model_field='currency', horizontal=True, to='custody.UserAddress'),
        ),
    ]
