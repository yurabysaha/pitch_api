from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^users$', views.UserList.as_view()),
    url(r'^users/(?P<user_id>[0-9]+)$', views.UserDetail.as_view()),
    url(r'^groups$', views.GroupList.as_view()),
    url(r'^groups/(?P<group_id>[0-9]+)$', views.GroupDetail.as_view()),
    url(r'^email_verify$', views.email_verify),
    url(r'^username_verify$', views.username_verify),
]
