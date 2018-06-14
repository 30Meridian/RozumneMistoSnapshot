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
            name='MvsWanted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('birth_date', models.DateField()),
                ('image', django_resized.forms.ResizedImageField(upload_to=petitions.models.get_file_path)),
                ('text', models.CharField(max_length=2000)),
                ('category_id', models.IntegerField(max_length=2)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'mvs_wanted',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MvsWantedCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('category', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'mvs_wanted_categories',
                'managed': False,
            },
        ),
    ]
