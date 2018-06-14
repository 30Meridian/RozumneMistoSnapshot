from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^clearfilter/+(?P<type>[a-z0-9].*)+/+(?P<code>[a-z0-9].*)$', clearFilter),
    url(r'^subscriptions$', sendSub),
    url(r'^payer/+(?P<payer_id>\d+)$', payer, name='payer'),
    url(r'^unsubscription/+(?P<code>\d+)$', ssunsubscription),
    url(r'^recipient/+(?P<receiver>\d+)$', recipient),
    url(r'^recipient/+(?P<receiver>\D+)$',  recipient),
    url(r'^ssdeactivate/+(?P<ss_id>\d+)$', ssdeactivate),
    url(r'^ssactivate/+(?P<ss_id>\d+)$', ssactivate),
    url(r'^ssdelete/+(?P<ss_id>\d+)$', ssdelete),
    url(r'^ssadd$', ssadd),
    url(r'^sendsub/+(?P<code>\d+)$', sendSub),
    url(r'^export$', exportToExcel),
    url(r'^exportrecipient/+(?P<receiver>[a-z0-9/\D].*)$', exportToExcelRecipient),
    url(r'^ssadd$', ssadd),



)


