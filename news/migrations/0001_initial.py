# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields
import news.models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('datetime_publish', models.DateTimeField()),
                ('title', models.CharField(max_length=150)),
                ('shortdesc', models.CharField(max_length=300)),
                ('text', ckeditor_uploader.fields.RichTextUploadingField()),
                ('mainimg', stdimage.models.StdImageField(upload_to=news.models.get_file_path)),
                ('publish', models.BooleanField()),
            ],
            options={
                'db_table': 'news',
                'managed': False,
            },
        ),
    ]
