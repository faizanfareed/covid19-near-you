from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.admin import AdminSite
from django.contrib import admin


class Covid19NearyouConfig(AppConfig):
    name = 'covid19nearyou'


    def ready(self):
        from . import receivers
        


class MyAdminConfig(AdminConfig):
    default_site = 'covid19nearyou.apps.MyAdminSite'


class MyAdminSite(admin.AdminSite):
    
    site_header = 'COVID-19 NEAR YOU  ADMINISTRATION'
    site_title = 'COVID-19 NEAR YOU ADMIN'
   
    index_title = 'COVID-19 NEAR YOU  MODELS'
    admin.empty_value_display = '**Empty**'
