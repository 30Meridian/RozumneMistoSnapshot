# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Edata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trans_id', models.IntegerField(blank=True, null=True)),
                ('trans_date', models.CharField(max_length=100, null=True, blank=True)),
                ('recipt_bank', models.CharField(max_length=150, null=True, blank=True)),
                ('recipt_name', models.CharField(max_length=100, null=True, blank=True)),
                ('amount', models.CharField(max_length=12, null=True, blank=True)),
                ('payment_details', models.CharField(max_length=250, null=True, blank=True)),
                ('payer_bank', models.CharField(max_length=150, null=True, blank=True)),
                ('payer_edrpou', models.CharField(max_length=8, null=True, blank=True)),
                ('recipt_edrpou', models.CharField(max_length=100, null=True, blank=True)),
                ('payer_name', models.CharField(max_length=100, null=True, blank=True)),
                ('recipt_mfo', models.IntegerField(blank=True, null=True)),
                ('payer_mfo', models.IntegerField(blank=True, null=True)),
                ('rand_ind', models.IntegerField()),
            ],
            options={
                'db_table': 'edata',
                'managed': False,
            },
        ),
    ]
