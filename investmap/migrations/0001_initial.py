from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields
import investmap.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('weunion', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestMapLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('data_time', models.DateTimeField(auto_now_add=True)),
                ('operation', models.CharField(max_length=32)),
                ('ip_address', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'investmap_logs',
            },
        ),
        migrations.CreateModel(
            name='InvestMapObject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100, verbose_name='Назва')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Опис')),
                ('price', models.CharField(max_length=16, verbose_name='Ціна')),
                ('address', models.CharField(max_length=100, verbose_name='Адреса')),
                ('metrics', models.CharField(max_length=50, verbose_name='Площа')),
                ('contacts', models.CharField(max_length=100, verbose_name='Контакти')),
                ('project_type', models.CharField(max_length=2, verbose_name="Тип об'єкту", default=('fb', 'Приміщення'), choices=[('fb', 'Приміщення'), ('fa', 'Ділянка'), ('cp', 'Інвестиційний проект')])),
                ('object_type', models.IntegerField(verbose_name="Тип об'єкта", default=0, choices=[(0, 'Приміщення'), (1, 'Ділянка')])),
                ('image', models.ImageField(verbose_name='', upload_to='investmap/')),
                ('document', models.FileField(verbose_name='', validators=[investmap.validators.validate_document_file_extension], upload_to='investmap/')),
                ('town', models.ForeignKey(to='weunion.Town')),
            ],
            options={
                'db_table': 'investmap_objects',
            },
        ),
        migrations.CreateModel(
            name='InvestMapPoint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('map_lon', models.CharField(max_length=64)),
                ('map_lat', models.CharField(max_length=64)),
                ('investmap_object', models.ForeignKey(to='investmap.InvestMapObject')),
            ],
            options={
                'db_table': 'investmap_points',
            },
        ),
        migrations.AddField(
            model_name='investmaplog',
            name='investmap_object',
            field=models.ForeignKey(to='investmap.InvestMapObject'),
        ),
        migrations.AddField(
            model_name='investmaplog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
