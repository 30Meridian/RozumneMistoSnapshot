# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import investmap.validators


class Migration(migrations.Migration):

    dependencies = [
        ('investmap', '0002_auto_20161205_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmaplog',
            name='investmap_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='investmap.InvestMapObject', null=True),
        ),
        migrations.AlterField(
            model_name='investmapobject',
            name='document',
            field=models.FileField(blank=True, upload_to='investmap/', verbose_name='', validators=[investmap.validators.validate_document_file_extension]),
        ),
        migrations.AlterField(
            model_name='investmapstats',
            name='param',
            field=models.CharField(max_length=64, verbose_name='Значення'),
        ),
        migrations.AlterField(
            model_name='investmapstats',
            name='title',
            field=models.CharField(max_length=64, verbose_name='Параметр'),
        ),
    ]
