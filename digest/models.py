import json

from django.db import models

from weunion.models import User


class UserSubscriptions(models.Model):
    user = models.ForeignKey(User)
    subscription = models.CharField(max_length=255)

    @property
    def filter_list(self):
        return json.loads(self.subscription)
