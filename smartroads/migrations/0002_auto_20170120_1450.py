# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smartroads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartroadsissues',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='smartroadsissues',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='smartroadsissues',
            name='resolution',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='smartroadsissues',
            name='what_to_do',
            field=ckeditor_uploader.fields.RichTextUploadingField(null=True, blank=True),
        ),
    ]
