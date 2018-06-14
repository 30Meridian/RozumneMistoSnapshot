# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_email_max_length'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='emailaddress',
            table='account_emailaddress',
        ),
        migrations.AlterModelTable(
            name='emailconfirmation',
            table='account_emailconfirmation',
        ),
    ]
