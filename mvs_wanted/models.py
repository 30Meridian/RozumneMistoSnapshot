from weunion.models import User, Town
import uuid
from stdimage.models import StdImageField
from django.db import models

#генерируем псевдоуникальный файлнейм для загружаемых изображений
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'mvs_wanted/%s' % filename


class MvsWanted(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    image = StdImageField(blank=True, upload_to=get_file_path, variations={
        'large': (600, 400),
        'thumbnail': {"width": 100, "height": 100, "crop": True}
    })
    text = models.CharField(max_length=2000)
    category = models.ForeignKey('MvsWantedCategories', db_column='category_id')
    create_date = models.DateTimeField(auto_now_add=True)
    owner_user = models.ForeignKey(User, db_column='owner_user')
    town = models.ForeignKey(Town, db_column='town')

    class Meta:
        managed = False
        db_table = 'mvs_wanted'


class MvsWantedCategories(models.Model):
    category = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mvs_wanted_categories'
