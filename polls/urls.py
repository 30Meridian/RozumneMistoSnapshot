from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from polls.views import PollDetailView, PollListView, \
    PollVoteView, PollCreateView, checktimeout, \
    PollDeleteView, PollUpdateView

urlpatterns = patterns('',
    url(r'^$', PollListView.as_view(), name='list'),
    url(r'^add/$', PollCreateView.as_view(), name='create' ),
    url(r'^delete/(?P<pk>\d+)$', PollDeleteView.as_view(), name='delete' ),
    url(r'^update/(?P<pk>\d+)$', PollUpdateView.as_view(), name='up' ),
    url(r'^(?P<pk>\d+)/$', PollDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/vote/$', PollVoteView.as_view(), name='vote'),
    url(r'^checktimeout/+(?P<secret>[0-9]+)$', checktimeout, name="checktimeout"),
)
