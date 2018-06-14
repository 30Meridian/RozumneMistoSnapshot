# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_resized.forms
import petitions.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Petitions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('image', django_resized.forms.ResizedImageField(upload_to=petitions.models.get_file_path)),
                ('text', models.CharField(max_length=1000)),
                ('claim', models.CharField(max_length=1000)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('resolution', models.CharField(max_length=3000, null=True, blank=True)),
            ],
            options={
                'db_table': 'petitions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PetitionsActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('datatime', models.DateTimeField()),
                ('activity', models.CharField(max_length=500)),
                ('user', models.CharField(max_length=500)),
                ('ip', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'petitions_activity',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PetitionsStatuses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'petitions_statuses',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PetitionsVoices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('block', models.CharField(max_length=1, null=True, blank=True)),
            ],
            options={
                'db_table': 'petitions_voices',
                'managed': False,
            },
        ),
    ]
