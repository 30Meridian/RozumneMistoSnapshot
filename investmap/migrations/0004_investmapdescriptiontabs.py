# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '0001_initial'),
        ('investmap', '0003_auto_20161205_1926'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestMapDescriptionTabs',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=32)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('town', models.ForeignKey(to='weunion.Town')),
            ],
            options={
                'db_table': 'investmap_descriptions',
            },
        ),
    ]
