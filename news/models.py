# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.


from django.db import models
from weunion.models import User, Town
from ckeditor_uploader.fields import RichTextUploadingField
from stdimage.models import StdImageField
import uuid

#генерируем псевдоуникальный файлнейм для загружаемых изображений
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'news/%s' % filename

class News(models.Model):
    town = models.ForeignKey(Town, db_column='town')
    author = models.ForeignKey(User, db_column='author')
    datetime = models.DateTimeField(auto_now_add=True)
    datetime_publish = models.DateTimeField()
    title = models.CharField(max_length=150)
    shortdesc = models.CharField(max_length=300)
    text = RichTextUploadingField()
    mainimg = StdImageField(upload_to=get_file_path, variations={
        'large': (600, 400),
        'thumbnail': {"width": 100, "height": 100, "crop": True}
    })
    publish = models.BooleanField()

    def __str__(self):
        return self.title
    class Meta:
        managed = False
        db_table = 'news'
        verbose_name = 'новину'
        verbose_name_plural = 'Новини'