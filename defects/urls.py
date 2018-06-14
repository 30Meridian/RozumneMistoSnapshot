from django.conf.urls import url, patterns
from . import views
urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^mydefects$',views.mydefects,name="mydefects"),
    url(r'^moderate$',views.moderate,name="moderate"),
    url(r'^list$',views.list,name="list"),
    url(r'^help$',views.help,name="help"),
    url(r'^rules$',views.rules,name="rules"),
    url(r'^ok$',views.ok,name="ok"),
    url(r'^(?P<issue_id>[0-9]+)$',views.card,name="card"),
    url(r'^(?P<issue_id>[0-9]+)/setSubcontractor$',views.setSubcontractor,name="setSubcontactor"),
    url(r'^(?P<issue_id>[0-9]+)/addComment$',views.addComment,name="addComment"),
    url(r'^(?P<issue_id>[0-9]+)/print$',views.printIssue,name="print"),
    url(r'^(?P<comment_id>[0-9]+)/(?P<issue_id>[0-9]+)/blockcomment$',views.blockcomment,name="blockcomment"),
    url(r'^add$',views.add, name="add"),
    #statuses:
    url(r'^(?P<issue_id>[0-9]+)/unsubscribe$',views.unsubscribe,name="unsubscribe"),#Исполнетель отказался от работ
    url(r'^(?P<issue_id>[0-9]+)/setFix$',views.setFix,name="setFix"),#Заявка виконана
    url(r'^(?P<issue_id>[0-9]+)/setFixModer$',views.setFixModer,name="setFixModer"),#Заявка виконана. Статус выставляэ модератор
    url(r'^(?P<issue_id>[0-9]+)/disapprove',views.disapprove,name="disapprove"),#Заявка відхилена модератором
    url(r'^(?P<issue_id>[0-9]+)/padding',views.padding,name="padding"),#Заявка прийнята виконавце у роботу
    url(r'^(?P<issue_id>[0-9]+)/hold',views.hold,name="hold"),#Заявка утримана(запланована)
    url(r'^(?P<issue_id>[0-9]+)/reopen',views.reopen,name="reopen"),#Заявка переоткрыта
]