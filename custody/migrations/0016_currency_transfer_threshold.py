# Generated by Django 2.1.2 on 2018-10-31 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custody', '0015_auto_20181018_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='transfer_threshold',
            field=models.PositiveIntegerField(default=1),
        ),
    ]