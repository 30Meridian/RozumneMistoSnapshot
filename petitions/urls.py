from django.conf.urls import url, patterns
from . import views

urlpatterns = [
    url(r'^help$', views.help, name="help"),
    url(r'^rules$', views.rules, name="rules"),
    url(r'^$', views.index, name="index"),

    url(r'^status/+(?P<status>[0-9]+)$',views.list,name="list"),
    url(r'^(?P<petition_id>[0-9]+)$',views.petition,name="petition"),
    url(r'^add$', views.add, name="add"),
    url(r'^approve/+(?P<petition_id>[0-9]+)$',views.approve,name="approve"),
    url(r'^returntoactive',views.returntoactive,name="returntoactive"),
    url(r'^disapprove',views.disapprove,name="disapprove"),
    url(r'^done',views.done,name="done"),
    url(r'^hidepetition',views.hidepetition,name="hidepetition"),
    url(r'^tomoderate/+(?P<petition_id>[0-9]+)$', views.tomoderate,name="tomoderate"),
    url(r'^test$', views.test,name="test"),
    url(r'^moderate$', views.moderate,name="moderate"),
    url(r'^checktimeout/+(?P<secret>[^\>]+)$', views.checktimeout,name="checktimeout"),
    url(r'^disvote/+(?P<petition_id>[0-9]+)$', views.disvote,name="disvote"),
    url(r'^vote/+(?P<petition_id>[0-9]+)$', views.vote,name="vote"),
    url(r'^checktimeout/+(?P<secret>[0-9]+)$', views.checktimeout, name="checktimeout"),
    url(r'^ban/+(?P<user_id>[0-9]+)/(?P<petition_id>[0-9]+)/(?P<vote_id>[0-9]+)$',views.ban,name="ban"),
    url(r'^print/+(?P<petition_id>[0-9]+)$', views.print, name="print"),
    url(r'^onconsideration/+(?P<petition_id>[0-9]+)$', views.onconsideration, name="onconsideration"),
]