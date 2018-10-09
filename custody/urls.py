from django.conf.urls import url, include
from django.urls import path

from rest_framework.schemas import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
  # website
  url(r'^$', get_schema_view()),
  path("<slug:coin>/status", views.Status.as_view(), name='status'),
]

urlpatterns += staticfiles_urlpatterns()