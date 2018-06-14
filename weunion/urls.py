from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.conf import settings
from django.views.decorators.cache import never_cache

from ckeditor_uploader import views as viewsck

from . import views, urls_modules, urls_index
from .admin_site import CustomAdminSite

admin.site = CustomAdminSite()
admin.autodiscover()

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^check_user/$', views.check_user, name="check_user"),
    url(r'^edrpou_count/$', views.edrpou_count, name="edrpou_count"),
    url(r'^profile_change/',views.profile_change,name="profileChange"),
    url(r'^admin_rm/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^crowdfunding/', include('crowdfunding.urls')),
    url(r'^budgetuchastiya/', views.budgetuchastiya, name="budgetuchastiya"),
    url(r'^defects/', views.defects, name="defects"),
    url(r'^donors/', views.donors, name="donors"),
    url(r'^edata/', views.edata, name="edata"),
    url(r'^flats/', views.flats, name="flats"),
    url(r'^igov/', views.igov_2, name="igov"),
    url(r'^medicines/', views.medicines, name="medicines"),
    url(r'^news/', views.news, name="news"),
    url(r'^openbudget/', views.openbudget, name="openbudget"),
    url(r'^petitions/', views.petitions, name="petitions"),
    url(r'^polls/', views.polls, name="polls"),
    url(r'^prozorro/', views.prozorro_2, name="prozorro"),
    url(r'^smartroads/', views.smartroads, name="smartroads"),
    url(r'^mvs_wanted/', views.mvs_wanted, name="static_mvs_wanted"),
    url(r'^moderator/$', views.moderator, name="moderator"),
    url(r'^moderator/zvit', views.moderatorsZvit, name="moderatorsZvit"),
    url(r'^towns/+(?P<region_ref>[0-9]+)', views.towns, name="towns"),
    url(r'^choosetown/+(?P<townid>[0-9]+)', views.choosetown, name="choosetown"),
    url(r'^gromadasvillges/+(?P<gromada_id>[0-9]+)', views.gromadasVillages, name="gromadasvillges"),
    url(r'^regions/', views.regions, name="regions"),
    url(r'^gettown', views.gettown, name="gettown"),
    url(r'^about', views.about),
    url(r'^help', views.help),
    url(r'^getoutfromtown', views.getoutfromtown),
    url(r'^livestream', views.livestream, name='livestream'),
    url(r'^map', views.map),
    url(r'^partners', views.partners),
    url(r'^decentralization', views.decentralization),
    url(r'^contacts',views.contacts),
    url(r'^user_agreement',views.useragreement),
    url(r'^join',views.join),
    url(r'^api/',include('smartapi.urls', namespace='smartapi')),
    url(r'^rating',views.rating),
    url(r'^rules',views.rules),
    url(r'^test', views.test),
    url(r'^index/', include(urls_index, namespace='first_page')),
    url(r'^confirmyouremail',views.confirmyouremail),
    url(r'^profile/karma/+(?P<user_id>[0-9]+)',views.karma, name="karma"),
    url(r'^profile/+(?P<user_id>[0-9]+)',views.profile, name="profile"),
    url(r'^profile/userban/+(?P<user_id>[0-9]+)/+(?P<status>[0-9]+)',views.userban, name="userban"),
    url(r'^ckeditor/upload/', viewsck.upload, name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(viewsck.browse), name='ckeditor_browse'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT2, 'show_indexes':False}),
    url(r'^townslivesearch', views.townLiveSearch),
    url(r'^town/(?P<townredirect>.*)$', views.townRedirect),
    url(r'^lastnews$', views.last_news),
    url(r'^digest/', include('digest.urls')),
    url(r'(?P<townslug>[a-z\_]+)/',include(urls_modules)),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^add_message$', views.add_message_to_session, name='add_message'),
    url(r'^filter-cities$', views.filter_cities, name='filter-cities'),
    url(r'^eng$', views.eng_index)

]
