# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartroadsIssues',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500, blank=True, null=True)),
                ('what_to_do', models.CharField(max_length=500, blank=True, null=True)),
                ('cost', models.CharField(max_length=15, blank=True, null=True)),
                ('resolution', models.CharField(max_length=100, blank=True, null=True)),
                ('done_date', models.DateTimeField(null=True, blank=True)),
                ('created_date', models.DateTimeField()),
                ('address', models.IntegerField()),
                ('lat', models.CharField(max_length=25)),
                ('lon', models.CharField(max_length=25)),
                ('isblock', models.IntegerField()),
            ],
            options={
                'db_table': 'smartroads_issues',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SmartroadsStatuses',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'smartroads_statuses',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='smartroadsissues',
            name='status_ref',
            field=models.ForeignKey(to='smartroads.SmartroadsStatuses', db_column='status_ref'),
        ),
        migrations.AddField(
            model_name='smartroadsissues',
            name='town_ref',
            field=models.ForeignKey(to='weunion.Town', db_column='town_ref'),
        ),
        migrations.AddField(
            model_name='smartroadsissues',
            name='user_ref',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column='user_ref'),
        ),
    ]
