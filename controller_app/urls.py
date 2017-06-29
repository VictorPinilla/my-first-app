from django.conf.urls import include, url
from . import views

urlpatterns = [
   url(r'^controller$', views.controller_class.as_view()),

]
