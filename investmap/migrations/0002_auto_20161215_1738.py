# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields
import django.db.models.deletion
import investmap.validators


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '__first__'),
        ('investmap', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestMapDescriptionTabs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=32, unique=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('town', models.ForeignKey(to='weunion.Town')),
            ],
            options={
                'db_table': 'investmap_descriptions',
            },
        ),
        migrations.CreateModel(
            name='InvestMapStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(verbose_name='Параметр', max_length=64)),
                ('param', models.CharField(verbose_name='Значення', max_length=64)),
                ('town', models.ForeignKey(to='weunion.Town')),
            ],
            options={
                'db_table': 'investmap_stats',
            },
        ),
        migrations.AlterField(
            model_name='investmaplog',
            name='investmap_object',
            field=models.ForeignKey(to='investmap.InvestMapObject', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='investmapobject',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='investmapobject',
            name='document',
            field=models.FileField(verbose_name='', upload_to='investmap/', blank=True, validators=[investmap.validators.validate_document_file_extension]),
        ),
    ]
