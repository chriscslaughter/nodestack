# Generated by Django 2.1.2 on 2018-10-12 20:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custody', '0005_auto_20181012_2013'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useraddress',
            unique_together={('user', 'currency')},
        ),
    ]