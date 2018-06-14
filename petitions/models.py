import datetime
import uuid

from django.db import models

from weunion.models import User, Town
from stdimage.models import StdImageField


#генерируем псевдоуникальный файлнейм для загружаемых изображений
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'petitions/%s' % filename


class Petitions(models.Model):
    title = models.CharField(max_length=255)
    image = StdImageField(blank=True, upload_to=get_file_path, variations={
        'large': (600, 400),
        'thumbnail': {"width": 100, "height": 100, "crop": True}
    })
    text = models.CharField(max_length=1000)
    claim = models.CharField(max_length=1000)
    status = models.ForeignKey('PetitionsStatuses', db_column='status')
    create_date = models.DateTimeField(auto_now_add=True)
    owner_user = models.ForeignKey(User, db_column='owner_user')
    resolution = models.CharField(max_length=3000, blank=True, null=True)
    town = models.ForeignKey(Town, db_column='town')
    when_approve = models.DateTimeField()
    anonymous = models.BooleanField()

    @property
    def days_left(self):
        time_delta = self.when_approve + datetime.timedelta(days=self.town.pet_days+1) - datetime.datetime.now()
        if(time_delta.days >= 1):
            return int(str(time_delta.days))
        else:
            return "<1"

    class Meta:
        managed = False
        db_table = 'petitions'

    #проверочка для того что бы вывести в списке петиций голосовал ли пользователь или нет за петициию
    def voters(self):
        return [v.user for v in self.petitionsvoices_set.all()]

    #проверочка что бы вывести количество голосов для петиций без заблокированых
    def vote_count(self):
        return self.petitionsvoices_set.exclude(block = 1).all().count()



class PetitionsActivity(models.Model):
    datatime = models.DateTimeField(auto_now_add=True)
    activity = models.CharField(max_length=500)
    user = models.ForeignKey(User, db_column='user')
    ip = models.CharField(max_length=500)
    petition = models.ForeignKey(Petitions, db_column='petition')

    class Meta:
        managed = False
        db_table = 'petitions_activity'


class PetitionsStatuses(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'petitions_statuses'


class PetitionsVoices(models.Model):
    petition = models.ForeignKey(Petitions, db_column='petition', blank=True, null=True)
    user = models.ForeignKey(User, db_column='user', blank=True, null=True)
    block = models.CharField(max_length=1, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'petitions_voices'