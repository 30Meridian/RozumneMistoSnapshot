from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from stdimage.models import StdImageField
import uuid

from weunion.models import Town

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'polls/%s' % filename


class Poll(models.Model):
    question = models.CharField(max_length=255, verbose_name='Питання')
    description = models.TextField(blank=True,verbose_name='Опис')
    town = models.ForeignKey(Town, db_column='town_ref', related_name="town",verbose_name='Місто')
    date_start = models.DateField(verbose_name='Дата початку')
    date_end = models.DateField(verbose_name='Дата закінчення')
    active = models.BooleanField(default=True,verbose_name='Активне')
    archive = models.BooleanField(default=False,verbose_name='Архівне')


    class Meta:
        verbose_name = "Опитування"
        verbose_name_plural = "Опитування"

    def count_choices(self):
        return self.choice_set.count()

    def count_total_votes(self):
        result = 0
        for choice in self.choice_set.all():
            result += choice.count_votes()
        return result

    def can_vote(self, user):
        if user:
            if(self.vote_set.filter(user=user).exists() or self.active == False or self.archive == True or (user.towns.all()[0] != self.town)):
                return False
            else:
                return True
        else:
            return False

    def has_image(self):
        if self.choice_set.all().exclude(image=''):
            return True
        else:
            return False

    def __str__(self):
        return self.question

    def clean(self):
        if not self.question:
            super(Poll, self).clean()
        elif self.date_start >= self.date_end :
            raise ValidationError(
                'Дата початку голосування не може бути більшою або рівною даті закінчення!')


class Choice(models.Model):
    poll = models.ForeignKey(Poll, verbose_name='Опитування')
    choice = models.CharField(max_length=255, verbose_name='Варіант', blank=True)
    image = StdImageField(blank=True, upload_to=get_file_path, variations={
        'large': (600, 400),
        'thumbnail': {"width": 300, "height": 300, "crop": True}
    }, verbose_name='Зображення')

    def count_votes(self):
        return self.vote_set.count()

    def __unicode__(self):
        return self.choice

    def __str__(self):
        return self.choice

    class Meta:
        ordering = ['choice']
        verbose_name = 'Варіант'
        verbose_name_plural = 'Варіанти'

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Користувач")
    poll = models.ForeignKey(Poll, verbose_name="Опитування")
    choice = models.ForeignKey(Choice, verbose_name="Варіант")

    def __str__(self):
        return 'Голос для %s' % (self.choice)

    class Meta:
        unique_together = (('user', 'poll'))
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоси'