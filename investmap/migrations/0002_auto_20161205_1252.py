# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '__first__'),
        ('investmap', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestMapStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('param', models.CharField(max_length=64)),
                ('town', models.ForeignKey(to='weunion.Town')),
            ],
            options={
                'db_table': 'investmap_stats',
            },
        ),
        migrations.AlterField(
            model_name='investmapobject',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
