"""URL conf for blog app."""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.post_list, name='post_list'),
]
