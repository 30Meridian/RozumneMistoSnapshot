from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField

from weunion.models import User, Town

from .validators import validate_document_file_extension

PROJECT_TYPES = [
    ('fb', 'Приміщення'),
    ('fa', 'Ділянка'),
    ('cp', 'Інвестиційний проект')
]

OBJECT_TYPES = [
    (0, 'Приміщення'),
    (1, 'Ділянка')
]


class InvestMapObject(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Назва')
    description = RichTextUploadingField()
    price = models.CharField(max_length=16, verbose_name='Ціна')
    address = models.CharField(max_length=100, verbose_name='Адреса')
    metrics = models.CharField(max_length=50, verbose_name='Площа')
    contacts = models.CharField(max_length=100, verbose_name='Контакти')

    project_type = models.CharField(max_length=2, choices=PROJECT_TYPES,
                                    default=PROJECT_TYPES[0], verbose_name='Тип об\'єкту')
    object_type = models.IntegerField(choices=OBJECT_TYPES, default=0, verbose_name='Тип об\'єкта')

    image = models.ImageField(upload_to='investmap/', verbose_name='')
    document = models.FileField(upload_to='investmap/', validators=[validate_document_file_extension],
                                verbose_name='', blank=True)

    @property
    def lat_lng(self):
        query = InvestMapPoint.objects.filter(investmap_object=self)
        count = query.count()
        result = []
        if count == 1:
            result = query.first().lat_lng()
        elif count > 1:
            result = [coordinate.lat_lng() for coordinate in query]
        return result

    class Meta:
        db_table = 'investmap_objects'


class InvestMapPoint(models.Model):
    investmap_object = models.ForeignKey(InvestMapObject, on_delete=models.CASCADE)
    map_lon = models.CharField(max_length=64)
    map_lat = models.CharField(max_length=64)

    def lat_lng(self):
        return {'lat': float(self.map_lat), 'lng': float(self.map_lon)}

    class Meta:
        db_table = 'investmap_points'


class InvestMapLog(models.Model):
    investmap_object = models.ForeignKey(InvestMapObject, on_delete=models.SET_NULL, null=True)
    data_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation = models.CharField(max_length=32)
    ip_address = models.CharField(max_length=32)

    class Meta:
        db_table = 'investmap_logs'


class InvestMapStats(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, verbose_name='Параметр')
    param = models.CharField(max_length=64, verbose_name='Значення')

    class Meta:
        db_table = 'investmap_stats'


class InvestMapDescriptionTabs(models.Model):
    slug = models.CharField(max_length=32, unique=True)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    description = RichTextUploadingField()

    class Meta:
        db_table = 'investmap_descriptions'
