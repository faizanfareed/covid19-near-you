
# COVID-19 NEAR YOU

  

Find confirmed cases in 1,2 and 3 km and quarantine center in 10 Km radius range based on user given location, give  some useful advises and informational links,  and help  officials to control covid19 transmission.  


*    Find users zone if they are in Red, Yellow or Green zone based on confirmed case aorund them.
*    Give advices to people what they should do or not if they are in infected region or not.
*    Show cluster of COVID-19 regions for officals to take right decisions. And  for public  to take  appropriate precautions.Officials can
      * Easily identify infected regions, and then  impose lockdown and run awareness compaign.
      * (Local authorities) can take quick and real time decision. 
      * Identify those regions where no of cases increasing.
*    Show nearest confirmed case and Quarantine center point (address , distance (from user location) and radius range).      
*    Show  total no of confirmed cases  and no of points in different ranges  around user.
*    Provides WHO (World Health Organization) and  National  website links for latest information  and some other useful links  
       * [Myth busters]( https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters)
       * [When and how to use masks](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/when-and-how-to-use-masks)
       * [Advice for public]( https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)
       * [Advocacy](    https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/healthy-parenting)
* Users can also check other regions in case of if they wanna go or someone coming from infected region based on result they will take right decsion and appropriate precautions.
 

If people already know about infected regions and people of these regions transmitting the virus,then they will avoid them, (infected regions and thier people as well) so they will be definitely taking necessary precautions.
 
**Must Read [How COVID-19 NEAR YOU app can help to control transmission ? ](https://github.com/FaizanFareed/COVID-19-NEAR-YOU/blob/master/faq.md)**
    
***


[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) 

[![Generic badge](https://img.shields.io/badge/license-MIT-success.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://shields.io/)

[![Open Source Love svg3](https://badges.frapsoft.com/os/v3/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/) 




<a name=""></a>
# Table of contents

- [COVID-19 NEAR YOU](#covid-19-near-you)
- [Requirements](#requirements)
- [Virtual environment](#virtual-environment)
- [Installation](#installation)
- [Setup](#setup)
- [App links](#app-links)
- [FAQ](#faq)
- [License](#license)
- [Contributing](#contributing)
- [Built with](#built-with)
- [Open source software used in this project](#open-source-software-used-in-this-project)

**Note :**
Leaflet auto navigation not giving precise location of user that's why we are getting user precise location manually. 
          
<a name="requirements"></a>
# Requirements 
 
- [Python](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/stable/installing/)
- [Redis](https://redis.io/download)
- [MySQL](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/)


   

<a name="virtual-environment"></a>
# Virtual environment

  
Create new directory

```bash
mkdir covid19
```
Change directory

```bash
cd covid19/
```
Create virtual environment

```bash
python3 -m venv env
```
Activate virtual environment
```bash
# Windows:
env\Scripts\activate.bat

# On Unix or MacOS, run:
source env/bin/activate
```


<a name="installation"></a>
# Installation

Clone repository

```bash
git clone git@github.com:FaizanFareed/COVID-19-NEAR-YOU.git
```
Change directory
```bash
cd COVID-19-NEAR-YOU/
```

Create media directory 
```bash
mkdir -p media/location
```
Install all dependencies
```bash
pip install -r requirements.txt
```
Create new project with name **covid19**.

```python
# Don't forget to miss "." .
django-admin startproject covid19 . 
```

<a name="setup"></a>
# Setup  

Add  MySQL database config into covid19/settings.py. And delete by default SQLite database directive (config). 
  
```python
# covid19/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

Add  Email provider config into covid19/settings.py


```python
# covid19/settings.py

# Console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email provider
#DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
#EMAIL_BACKEND = config('EMAIL_BACKEND')
#EMAIL_HOST = config('EMAIL_HOST')
#EMAIL_USE_TLS = config('EMAIL_USE_TLS',cast=bool)
#EMAIL_PORT = config('EMAIL_PORT',cast=int)
#EMAIL_HOST_USER = config('EMAIL_HOST_USER')
#EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```



Add Redis config into covid19/settings.py

  

```python
# covid19/settings.py

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config('REDIS_LOCATION_URL'), # Redis url
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "REDIS_CLIENT_KWARGS": {"decode_responses": True, 'charset':"utf-8"},
        }
    },"KEY_PREFIX" : "covid19",
}

# Storing session in Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
DJANGO_REDIS_IGNORE_EXCEPTIONS = True

```

  

Copy this and  paste into covid19/urls.py

  

```python
# covid19/urls.py

from django.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    ... # Others if any 

    # Admin password reset urls
    path('admin/password_reset/',auth_views.PasswordResetView.as_view(),name='admin_password_reset',),
    path('admin/password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done',),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm',),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete',),
    path('admin/', include('django.contrib.auth.urls')),

    # covid19nearyou app urls
    path('',include('covid19nearyou.urls'))
]
```

  
Copy this and paste into covid19/settings.py


```python
# covid19/settings.py

#Static and media urls and root directory 

# Static files 
STATIC_URL = '/files/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"),]

# Media files
MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/location-points/'
```


Change your time zone from covid19/settings.py.

```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi' # your timezone
```
  

Add setting_constants context processer and template path into **TEMPLATES** directive in covid19/settings.py

  

```python
# covid19/settings.py

TEMPLATES = [
        {
            ... # others 
            'DIRS': [os.path.join(BASE_DIR, 'templates')], # copy this  
            'OPTIONS': {
                ... # others
                'context_processors': [
                    ... # others
                    'covid19nearyou.context_processors.setting_constants', # copy this 
                ],
            },
        },
    ]
```

  
  
  
Copy these and  paste into covid19/urls.py


```python
# covid19/urls.py

from django.conf import settings
from django.conf.urls.static import static
```
Add static and media path 

```python
# covid19/urls.py

urlpatterns = [
        ... # urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # copy and add this at the end of urlpatterns 

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # copy this 
```

  
Add  **covid19nearyou** app and MyAdminConfig into INSTALLED_APPS directive in covid19/settings.py

  

```python
# covid19/settings.py

INSTALLED_APPS = [
    ... # others apps 
    'covid19nearyou.apps.Covid19NearyouConfig',
    'covid19nearyou.apps.MyAdminConfig',
]
```

  
Copy all directives from [covid19_settings_variables](https://github.com/FaizanFareed/COVID-19-NEAR-YOU/blob/master/covid19nearyou/covid19_settings_variables.py)
and paste  into covid19/settings.py. And change these directives according to your requirements. 

```python
# covid19/settings.py

... # others directives 

LOCATION_CACHE_BATCH_SIZE = 100
...
# All directives of covid19_settings_variables.py file goes here
```
Change  country name in covid19/settings.py
```python
COUNTRY_NAME = 'PAKISTAN' # your country name  
```

Migrate


```python
python manage.py  migrate
```

Create superuser

```python
python manage.py createsuperuser

username : #enter username
Email address: # enter your emailaddress
Password: #enter your password
Password (again): # again enter your password
```

Run server

```python
python manage.py runserver
```

*** 

<a name="App links"></a>
#  App links 

- Index page or Map  : 
 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Dashboard : [http://127.0.0.1:8000/covid19-dashboard/](http://127.0.0.1:8000/covid19-dashboard/)
- Admin panel :  [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- App configuration :  [http://127.0.0.1:8000/settings-configuration/](http://127.0.0.1:8000/settings-configuration/) 
- Help/How to use : [http://127.0.0.1:8000/help/](http://127.0.0.1:8000/help/)



<a name="faq-and-howtouse"></a>
# FAQ 

- [FAQ](https://github.com/FaizanFareed/COVID-19-NEAR-YOU/blob/master/faq.md)
- Ask here  [https://github.com/FaizanFareed/COVID-19-NEAR-YOU/issues](https://github.com/FaizanFareed/COVID-19-NEAR-YOU/issues) 


<a name="license"></a>
# License

[![Generic badge](https://img.shields.io/badge/license-MIT-success.svg)](https://shields.io/)

License under a [MIT License](https://choosealicense.com/licenses/mit/).


<a name="contributing"></a>
# Contributing 

If you have any suggestions , request new features ,found bugs,  or  you can start discussion  at [https://github.com/FaizanFareed/COVID-19-NEAR-YOU/issues](https://github.com/FaizanFareed/COVID-19-NEAR-YOU/issues)

- Fork, clone or make a pull requset to this repository. 
  
<a name="built-with"></a>
# Built with

- Django (Python)
- Redis 
- MySQL
- Leaflet 
- Semantic UI 
- JQuery 


# Open source software used in this project 

Open soruce software license

- Leaflet [ BSD 2-Clause "Simplified" License](https://github.com/Leaflet/Leaflet/blob/master/LICENSE)
- Sementic UI [MIT License](https://github.com/Semantic-Org/Semantic-UI/blob/master/LICENSE.md)

