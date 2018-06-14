from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list', views.list_base, name='list'),
    url(r'^create$', view=views.create, name='create'),
    url(r'^edit/(?P<investmap_pk>[0-9]+)$', view=views.edit, name='edit'),
    url(r'^detail/(?P<investmap_pk>[0-9]+)$', view=views.detail, name='detail'),
    url(r'^delete/(?P<investmap_pk>[0-9]+)$', view=views.delete, name='delete'),
    url(r'^iframe_list$', view=views.iframe_list_base, name='iframe_list'),
    url(r'^ajax$', view=views.ajax, name='ajax'),
    url(r'^add_stats', view=views.add_stats, name='add_stats'),
    url(r'^delete_stats/(?P<investstat_pk>[0-9]+)$', view=views.delete_stats, name='delete_stats'),
    url(r'^edit_description/(?P<slug>[0-9a-zA-Z_-]+)$', view=views.edit_description, name='edit_description'),
    url(r'^export_to_exel$', view=views.export_to_exel, name='export_to_exel'),
]