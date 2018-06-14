from __future__ import unicode_literals
from django.db import models
#we're going utilize this class
from weunion.models import User, Town, Regions, Subcontractors
from django.core.exceptions import MultipleObjectsReturned

class Attachements(models.Model):
    message_ref = models.ForeignKey('Messages', db_column='message_ref')
    document_ref = models.ForeignKey('Documents', db_column='document_ref')

    class Meta:
        managed = False
        db_table = 'attachements'


class CommentAttachements(models.Model):
    comment_ref = models.ForeignKey('Comments', db_column='comment_ref')
    document_ref = models.ForeignKey('Documents', db_column='document_ref')

    class Meta:
        managed = False
        db_table = 'comment_attachements'


class Comments(models.Model):
    title = models.CharField(max_length=512, blank=True, null=True)
    body = models.CharField(max_length=2048, blank=True, null=True)
    attachements = models.IntegerField()
    issue_ref = models.ForeignKey('Issues', db_column='issue_ref')
    owner_ref = models.ForeignKey(User, db_column='owner_ref', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    block = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'comments'


class Documents(models.Model):
    owner_ref = models.ForeignKey(User, db_column='owner_ref')
    file_ref = models.ForeignKey('Files', db_column='file_ref')
    name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    type_name = models.CharField(max_length=45)
    size = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'documents'


class Files(models.Model):
    body = models.CharField(max_length=10485760)

    class Meta:
        managed = False
        db_table = 'files'


class IssueFiles(models.Model):
    issue_ref = models.ForeignKey('Issues', db_column='issue_ref')
    document_ref = models.ForeignKey(Documents, db_column='document_ref')

    class Meta:
        managed = False
        db_table = 'issue_files'


class Issues(models.Model):
    owner_ref = models.ForeignKey(User, db_column='owner_ref',verbose_name="Owner")
    parent_task_ref = models.ForeignKey('self', db_column='parent_task_ref')
    status = models.IntegerField()
    assigned_to = models.ForeignKey(Subcontractors, db_column='assigned_to')
    town_ref = models.ForeignKey(Town, db_column='town_ref',verbose_name="Мiсто")
    title = models.CharField(max_length=255,verbose_name="Назва")
    description = models.CharField(max_length=2048,verbose_name="Опис")
    address = models.CharField(max_length=512,verbose_name="Адреса")
    map_lon = models.CharField(max_length=128, blank=True, null=True)
    map_lat = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'issues'
        verbose_name = 'проблему'
        verbose_name_plural = 'Проблеми'

    def __str__(self):
        return self.title

    #next issue
    def __next(self):
        try:
            return Issues.objects.get(parent_task_ref=self.id)
        except Issues.DoesNotExist:
            return None
        except MultipleObjectsReturned: #TODO: И что это, почему не в импорте ? #not sure yet what to do if there's multiple references which should not be there
            Issues.objects.filter(parent_task_ref=self.id)[0]

    def getTree(self):
        tree=[]
        if(not self.firstIssue()):
            return self.parent_task_ref.getTree()
        tree.append(self)
        issue=self.__next()
        while(issue is not None):
            tree.append(issue)
            issue=issue.__next()
        return tree

    def getFirst(self):
         return self.getTree()[0]


    def last_issue(self):
        return self.getTree()[-1]

    def firstIssue(self):
        try:
            self.parent_task_ref
            return False
        except:
            return True

    #статусы для карточки
    ISSUE_STATUS={"BY_ID":["На модерацii","Вiдкрита","Виконана","Відхилена модератором","Прийнята до виконання","Запланована","Арбiтраж"]}

    def statusName(self):
        return self.ISSUE_STATUS["BY_ID"][self.status]

    def statusNameFirst(self):
        return self.ISSUE_STATUS["BY_ID"][self.getTree()[-1].status]

    def hasComments(self):
        if(self.comments_set.count()>0):
            return True
        else:
            return False

class Messages(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=2048, blank=True, null=True)
    attachments = models.IntegerField()
    sender_ref = models.ForeignKey(User, related_name='auth_user_sender_ref', db_column='sender_ref')
    rcpt_ref = models.ForeignKey(User, related_name='auth_user_rcpt_ref', db_column='rcpt_ref')
    hidden_sender = models.IntegerField()
    hidden_rcpt = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'messages'