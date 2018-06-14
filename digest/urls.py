from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^send_digest/+(?P<secret>[0-9a-zA-Z_-]+)', views.send_digest, name='send_digest'),
    url(r'^unsubscribe/+(?P<user_id>[0-9]+)', views.unsubscribe, name='unsubscribe'),
]