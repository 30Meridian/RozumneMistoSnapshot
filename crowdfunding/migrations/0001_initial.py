# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields
import crowdfunding.models
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrowdfoundingDonates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField()),
                ('datetime', models.DateTimeField()),
                ('user_comment', models.CharField(max_length=1000)),
                ('isblocked', models.IntegerField()),
            ],
            options={
                'db_table': 'crowdfounding_donates',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CrowdfoundingProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, blank=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('ifnotcollect', models.TextField(blank=True, null=True)),
                ('money_goal', models.IntegerField()),
                ('image', stdimage.models.StdImageField(upload_to=crowdfunding.models.get_file_path)),
                ('isblocked', models.IntegerField()),
            ],
            options={
                'db_table': 'crowdfounding_projects',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CrowdfoundingStatuses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'crowdfounding_statuses',
                'managed': False,
            },
        ),
    ]
