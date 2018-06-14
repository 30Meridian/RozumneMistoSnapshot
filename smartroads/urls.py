from django.conf.urls import url, patterns
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),#Первая страничка
    url(r'^add$', views.add, name="add"),#Страничка добавления зоны
    url(r'^edit/(?P<issue_id>[0-9]+)$', views.edit, name="edit"),
    url(r'^delete/(?P<issue_id>[0-9]+)$', views.delete_issue, name="delete"),
    url(r'(?P<issue_id>[0-9]+)$', views.card, name="card"), #Страничка карточки зоны
]