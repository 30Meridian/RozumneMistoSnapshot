from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.first_page, name='index'),
    url(r'^projects_about', views.projects_about, name="projects_about"),
    url(r'^contacts', views.contacts_new, name="contacts"),
    url(r'^team', views.new_team, name="team"),
    url(r'^for_local_goverment', views.for_local_goverment, name="for_local_goverment"),
    url(r'^for_citizens', views.for_citizens, name="for_citizens"),
    url(r'^how_to', views.how_to, name="how_to"),
    url(r'^results', views.statistics, name="results"),
    url(r'^rules', views.first_page_rules, name='rules'),
    url(r'^login', views.login_page, name='login'),
    url(r'^signup', views.signup_page, name='signup'),
    url(r'^password_reset$', views.password_reset_page, name='password_reset'),
    url(r'^password_reset_done$', views.password_reset_done_page, name='password_reset_done'),
    url(r'^success_signup', views.success_signup, name='success_signup'),
    url(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views.password_reset_from_key_page,
        name="reset_password_from_key"),
    url(r'^password/reset/key/done/$', views.password_reset_from_key_done_page,
        name="reset_password_from_key_done"),

]