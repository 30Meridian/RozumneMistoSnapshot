# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('phone', models.CharField(verbose_name='Номер телефону', max_length=50, null=True)),
                ('middle_name', models.CharField(verbose_name='По батькові', max_length=50)),
            ],
            options={
                'managed': False,
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AuthUserKarma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('points', models.IntegerField(blank=True, null=True)),
                ('forwhat', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'managed': False,
                'db_table': 'auth_user_karma',
            },
        ),
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=15, blank=True, null=True)),
                ('slug', models.CharField(max_length=15, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'modules',
            },
        ),
        migrations.CreateModel(
            name='Regions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'managed': False,
                'db_table': 'regions',
            },
        ),
        migrations.CreateModel(
            name='Subcontractors',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'subcontractors',
            },
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('is_active', models.IntegerField()),
                ('parameter', models.CharField(choices=[('amount', 'Сума транзакції (гривень)'), ('recipient_edrpou', 'ЄРДПОУ-код отримувача'), ('recipient_title', 'Назва отримувача (по масці)'), ('payer_edrpou', 'ЄРДПОУ-код платника')], max_length=50)),
                ('comparison', models.CharField(choices=[('==', 'Дорівнює (==)'), ('!=', 'Не дорівнює (!=)'), ('>', 'Більше (>)'), ('<', 'Менше (<)')], max_length=10)),
                ('value', models.CharField(max_length=50)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('gencode', models.CharField(max_length=30)),
            ],
            options={
                'managed': False,
                'db_table': 'subscriptions',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionsTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('is_active', models.IntegerField()),
                ('periodic', models.IntegerField()),
            ],
            options={
                'managed': False,
                'db_table': 'subscriptions_types',
            },
        ),
        migrations.CreateModel(
            name='Town',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=45, blank=True, null=True)),
                ('slug', models.CharField(max_length=50)),
                ('votes', models.IntegerField(default=0)),
                ('pet_days', models.IntegerField()),
                ('pet_number_templ', models.CharField(max_length=10, blank=True, null=True)),
                ('map_lon', models.CharField(max_length=128)),
                ('map_lat', models.CharField(max_length=128)),
                ('zoom', models.IntegerField(default=14)),
                ('map_radius', models.IntegerField()),
                ('menu', models.CharField(max_length=10000, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'town',
            },
        ),
        migrations.CreateModel(
            name='TownBanners',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('imgsource', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'town_banners',
            },
        ),
        migrations.CreateModel(
            name='TownBudgets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('body', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'town_budgets',
            },
        ),
        migrations.CreateModel(
            name='TownEdrpou',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=50)),
            ],
            options={
                'managed': False,
                'db_table': 'town_edrpou',
            },
        ),
        migrations.CreateModel(
            name='TownGromada',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'town_gromada',
            },
        ),
        migrations.CreateModel(
            name='TownsAdditions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('type', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('title', models.CharField(max_length=150, blank=True, null=True)),
                ('edata_period', models.IntegerField(default=7)),
                ('description', models.CharField(max_length=1000, blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'towns_additions',
            },
        ),
        migrations.CreateModel(
            name='TownsGromadasVillages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
            ],
            options={
                'managed': False,
                'db_table': 'towns_gromadas_villages',
            },
        ),
        migrations.CreateModel(
            name='TownTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
            ],
            options={
                'managed': False,
                'db_table': 'town_types',
            },
        ),
        migrations.CreateModel(
            name='TownAllowedModules',
            fields=[
                ('town', models.ForeignKey(blank=True, primary_key=True, to='weunion.Town', serialize=False, db_column='town')),
            ],
            options={
                'managed': False,
                'db_table': 'town_allowed_modules',
            },
        ),
    ]
