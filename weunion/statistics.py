import datetime

from weunion.models import User, Town
from news.models import News
from petitions.models import Petitions
from defects.models import Issues
from polls.models import Poll


def city_stats():
    users = []
    for town in Town.objects.all():
        count = User.objects.filter(towns=town).count()
        defects = Issues.objects.filter(town_ref=town, parent_task_ref=None).count()
        petitions = Petitions.objects.filter(town=town).count()
        news = News.objects.filter(town=town).count()
        polls = Poll.objects.filter(town=town).count()

        if count > 4 or defects > 0 or petitions > 0 or news > 0 or polls > 0:
            users.append((town.name, count, petitions, defects, news, polls))
    return users

# Нижче даний модуль містить функції які використовуються для генерації статистики
# Кожна функція має однаковий набір параметрів date_from - date_to, розміщених для зручності використання у зворотному
# порядку


def users_registered(date_to=datetime.datetime.now(), date_from=datetime.datetime.min):
    return User.objects.filter(date_joined__gte=date_from, date_joined__lte=date_to).count()


def news_published(date_to=datetime.datetime.now(), date_from=datetime.datetime.min):
    return News.objects.filter(datetime_publish__gte=date_from, datetime_publish__lte=date_to).count()


def petitions_created(date_to=datetime.datetime.now(), date_from=datetime.datetime.min):
    return Petitions.objects.filter(create_date__gte=date_from, create_date__lte=date_to).count()


def defects_created(date_to=datetime.datetime.now(), date_from=datetime.datetime.min):
    return Issues.objects.filter(created__gte=date_from, created__lte=date_to, parent_task_ref=None).count()


def polls_created(date_to=datetime.datetime.now(), date_from=datetime.datetime.min):
    return Poll.objects.filter(date_start__gte=date_from, date_start__lte=date_to).count()
