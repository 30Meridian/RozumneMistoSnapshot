from django.db import models
from weunion.models import Town, User

# Create your models here.

class Edata(models.Model):
    trans_id = models.IntegerField(blank=True, null=True)
    trans_date = models.CharField(max_length=100, blank=True, null=True)
    recipt_bank = models.CharField(max_length=150, blank=True, null=True)
    recipt_name = models.CharField(max_length=100, blank=True, null=True)
    amount = models.CharField(max_length=12, blank=True, null=True)
    payment_details = models.CharField(max_length=250, blank=True, null=True)
    payer_bank = models.CharField(max_length=150, blank=True, null=True)
    payer_edrpou = models.CharField(blank=True, null=True,max_length=8)
    recipt_edrpou = models.CharField(max_length=100, blank=True, null=True)
    payer_name = models.CharField(max_length=100, blank=True, null=True)
    recipt_mfo = models.IntegerField(blank=True, null=True)
    payer_mfo = models.IntegerField(blank=True, null=True)
    town_ref = models.ForeignKey(Town, db_column='town_ref', blank=True, null=True)
    rand_ind = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'edata'