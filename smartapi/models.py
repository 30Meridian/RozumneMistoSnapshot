from django.db import models
from weunion.models import User

class AuthUserApiKeys(models.Model):
    apikey = models.CharField(unique=True, max_length=33, blank=True, null=True)
    user_ref = models.ForeignKey(User, db_column='user_ref', unique=True, blank=True, null=True)
    date_create = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    isblock = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_user_api_keys'