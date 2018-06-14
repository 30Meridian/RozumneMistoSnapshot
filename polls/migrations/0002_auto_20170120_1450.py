# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import stdimage.models
from django.conf import settings
import polls.models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='choice',
            options={'verbose_name_plural': 'Варіанти', 'verbose_name': 'Варіант', 'ordering': ['choice']},
        ),
        migrations.AlterModelOptions(
            name='poll',
            options={'verbose_name_plural': 'Опитування', 'verbose_name': 'Опитування'},
        ),
        migrations.AlterModelOptions(
            name='vote',
            options={'verbose_name_plural': 'Голоси', 'verbose_name': 'Голос'},
        ),
        migrations.AddField(
            model_name='choice',
            name='image',
            field=stdimage.models.StdImageField(verbose_name='Зображення', blank=True, upload_to=polls.models.get_file_path),
        ),
        migrations.AlterField(
            model_name='choice',
            name='choice',
            field=models.CharField(verbose_name='Варіант', blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='choice',
            name='poll',
            field=models.ForeignKey(to='polls.Poll', verbose_name='Опитування'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='active',
            field=models.BooleanField(verbose_name='Активне', default=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='archive',
            field=models.BooleanField(verbose_name='Архівне', default=False),
        ),
        migrations.AlterField(
            model_name='poll',
            name='date_end',
            field=models.DateField(verbose_name='Дата закінчення'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='date_start',
            field=models.DateField(verbose_name='Дата початку'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='description',
            field=models.TextField(verbose_name='Опис', blank=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='question',
            field=models.CharField(verbose_name='Питання', max_length=255),
        ),
        migrations.AlterField(
            model_name='poll',
            name='town',
            field=models.ForeignKey(verbose_name='Місто', db_column='town_ref', related_name='town', to='weunion.Town'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.ForeignKey(to='polls.Choice', verbose_name='Варіант'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='poll',
            field=models.ForeignKey(to='polls.Poll', verbose_name='Опитування'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Користувач'),
        ),
    ]
