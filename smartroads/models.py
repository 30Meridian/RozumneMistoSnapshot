from django.db import models
from weunion.models import User, Town
from ckeditor_uploader.fields import RichTextUploadingField


class SmartroadsIssues(models.Model):
    title = models.CharField(max_length=100)
    description = RichTextUploadingField()
    what_to_do = RichTextUploadingField(blank=True, null=True)
    cost = models.CharField(max_length=15, blank=True, null=True)
    resolution = RichTextUploadingField(blank=True, null=True)
    done_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    user_ref = models.ForeignKey(User, db_column='user_ref')
    status_ref = models.ForeignKey('SmartroadsStatuses', db_column='status_ref')
    town_ref = models.ForeignKey(Town, db_column='town_ref')
    lat = models.CharField(max_length=25)
    lon = models.CharField(max_length=25)
    isblock = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'smartroads_issues'


class SmartroadsStatuses(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'smartroads_statuses'


