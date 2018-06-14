from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.redirectToSummary),
    url(r'^home/', views.index_town, name="home"),
    url(r'^news/', include('news.urls', namespace="news")),
    url(r'^edata/', include('edata.urls', namespace="edata")),
    url(r'^defects/', include('defects.urls', namespace="defects")),
    url(r'^petitions/', include('petitions.urls', namespace="petitions")),
    url(r'^budget/', views.budget, name="budget"),
    url(r'^apibudget/', views.budget_api, name="budget_api"),
    url(r'^moderators/$', views.moderators, name="moderators"),
    url(r'^rating',views.rating),
    url(r'^prozorro', views.prozorro, name="prozorro"),
    url(r'^igov',views.igov, name="igov"),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^donor',views.donor, name="donor"),
    url(r'^partners', views.partners),
    url(r'^smartroads/', include('smartroads.urls', namespace="smartroads")),
    url(r'^info/+(?P<url_param>[a-z]+)', views.getDocums),
    url(r'^mvs_wanted/', include('mvs_wanted.urls', namespace="mvs_wanted")),
    url(r'^investmap/', include('investmap.urls', namespace='investmap')),
    #url(r'(?P<brokenlink>[a-zA-Z]+)', views.errorPage),
]