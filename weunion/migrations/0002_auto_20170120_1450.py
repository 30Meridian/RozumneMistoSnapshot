# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='town',
            options={'verbose_name_plural': 'Міста', 'verbose_name': 'Місто', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='townbanners',
            options={'verbose_name_plural': 'Банер міста', 'verbose_name': 'Банер міста', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='townedrpou',
            options={'verbose_name_plural': 'Код ЄДРПОУ', 'verbose_name': 'Код ЄДРПОУ', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='towngromada',
            options={'verbose_name_plural': 'Громади', 'verbose_name': 'Громада', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='townsadditions',
            options={'verbose_name_plural': 'Додатки міста', 'verbose_name': 'Додаток міста', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='townsgromadasvillages',
            options={'verbose_name_plural': 'Населені пункти - сателіти', 'verbose_name': 'Населений пункт', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': 'Користувачі', 'verbose_name': 'користувач', 'managed': False},
        ),
    ]
