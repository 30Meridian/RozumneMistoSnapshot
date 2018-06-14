from django.conf.urls import url, patterns
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^category/+(?P<category>[0-9]+)$',views.list,name="list"),
    url(r'^(?P<mvs_wanted_id>[0-9]+)$',views.mvs_wanted,name="mvs_wanted"),
    url(r'^add$', views.add, name="add"),
    url(r'^delete/+(?P<mvs_wanted_id>[0-9]+)$',views.delete,name="delete"),
    url(r'^edit/+(?P<mvs_wanted_id>[0-9]+)$',views.edit,name="edit"),
    url(r'^print/+(?P<mvs_wanted_id>[0-9]+)$',views.print,name="print"),
]