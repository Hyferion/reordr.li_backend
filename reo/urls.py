from django.urls import path

from reo import views

urlpatterns = [
    path('shuffle', views.shuffle, name='shuffle'),
]
