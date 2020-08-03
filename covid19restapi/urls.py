from django.contrib import admin
from django.urls import path, include
from . import views





urlpatterns = [

        path('', views.index, name='restapi'),
        path('token', views.generate_token, name='generate_token'),


    ]