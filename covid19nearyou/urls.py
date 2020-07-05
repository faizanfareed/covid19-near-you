from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [

        path('', views.index, name='index_map'),
        path('help/', views.help, name='help'),
        path('settings-configuration/', views.settings_config, name='settings_config'),
        path('covid19-dashboard/', views.dashboard, name='dashboard'),
        path('add-to-file-new-and-expire-old-covid19-locations/', views.Add_To_File_New_And_Expire_Old_Covid19_Locations, name='Add_To_File_New_And_Expire_Old_Covid19_Locations'),
        path('cache-empty-add-geospatial-data-into-cache/', views.Cache_Failed_Add_Geospatial_Data_Into_Cache, name='Cache_Failed_Add_Geospatial_Data_Into_Cache'),
        path('ajax-request/', views.AJAX_find_covid19_near_you, name='AJAX_find_covid19_near_you'),


    ]