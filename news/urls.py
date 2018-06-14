from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add$', views.add, name="add"),
    url(r'^$', views.list, name="list"),
    url(r'^(?P<id>[0-9]+)$', views.article, name="article"),
    url(r'^delete/+(?P<id>[0-9]+)$', views.delete, name="delete"),
    url(r'^edit/+(?P<id>[0-9]+)$', views.edit, name="edit"),
    url(r'^publish/+(?P<id>[0-9]+)$', views.publish, name="publish"),
    url(r'^unpublish/+(?P<id>[0-9]+)$', views.unpublish, name="unpublish"),
    url(r'^suggest_news$', views.suggest_news, name='suggest_news'),
]