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
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['choice'],
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('archive', models.BooleanField(default=False)),
                ('town', models.ForeignKey(db_column='town_ref', related_name='town', to='weunion.Town')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.ForeignKey(to='polls.Choice')),
                ('poll', models.ForeignKey(to='polls.Poll')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='choice',
            name='poll',
            field=models.ForeignKey(to='polls.Poll'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'poll')]),
        ),
    ]
