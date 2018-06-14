from django.db import models
from weunion.models import User,Town
from ckeditor_uploader.fields import RichTextUploadingField
from stdimage.models import StdImageField
import uuid


#генерируем псевдоуникальный файлнейм для загружаемых изображений
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'crowdfunding/%s' % filename



class CrowdfoundingDonates(models.Model):
    project_ref = models.ForeignKey('CrowdfoundingProjects', db_column='project_ref')
    user_ref = models.ForeignKey(User, db_column='user_ref')
    amount = models.IntegerField()
    datetime = models.DateTimeField()
    user_comment = models.CharField(max_length=1000)
    isblocked = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'crowdfounding_donates'


class CrowdfoundingProjects(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    description = RichTextUploadingField()
    ifnotcollect = models.TextField(blank=True, null=True)
    user_owner_ref = models.ForeignKey(User, db_column='user_owner_ref', blank=True, null=True,related_name='user_owner_ref')
    moderator_approve_ref = models.ForeignKey(User, db_column='moderator_approve_ref', blank=True, null=True)
    town_ref = models.ForeignKey(Town, db_column='town_ref', blank=True, null=True)
    money_goal = models.IntegerField()
    image = StdImageField(upload_to=get_file_path, variations={
        'large': (960, 500),
        'thumbnail': {"width": 450, "height": 200, "crop": True}
    })
    status_ref = models.ForeignKey('CrowdfoundingStatuses', db_column='status_ref')
    isblocked = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'crowdfounding_projects'


class CrowdfoundingStatuses(models.Model):
    title = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'crowdfounding_statuses'

