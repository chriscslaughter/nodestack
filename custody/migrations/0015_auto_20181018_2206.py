# Generated by Django 2.1.2 on 2018-10-18 22:06

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custody', '0014_auto_20181018_2157'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='useraddress',
            unique_together={('user', 'currency'), ('address', 'currency')},
        ),
    ]