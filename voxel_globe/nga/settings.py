"""
Django settings for nga project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os import path, environ as env

BASE_DIR = path.dirname(path.dirname(__file__))

GEOS_LIBRARY_PATH=env['VIP_DJANGO_GEOS_LIBRARY_PATH'];
GDAL_LIBRARY_PATH=env['VIP_DJANGO_GDAL_LIBRARY_PATH'];
#This shoudl work in windows too?

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20hiyp8-=0+oan+sa(r$xz#j83jr5*13*(j_(a)9q234cynf+&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env['VIP_DJANGO_DEBUG']=='1'

TEMPLATE_DEBUG = env['VIP_DJANGO_TEMPLATE_DEBUG']=='1'

ALLOWED_HOSTS = env['VIP_DJANGO_ALLOWED_HOSTS'];

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'django.contrib.gis',
    'voxel_globe.meta',
    'voxel_globe.world',
    'voxel_globe.main',
    'voxel_globe.tiepoint',
    'voxel_globe.ingest',
    'voxel_globe.task',
    'voxel_globe.order.visualsfm',
    'django.contrib.staticfiles',
) #Staticfiles MUST come last, or else it might skip some files
  #at collectstatic deploy time!!!! This is one of the rare times
  #order matters

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'voxel_globe.nga.middleware.RequireLoginMiddleware',
)

ROOT_URLCONF = 'voxel_globe.nga.urls'

WSGI_APPLICATION = 'voxel_globe.nga.wsgi.application'

SERIALIZATION_MODULES = { 'geojson' : 'voxel_globe.serializers.geojson' }

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    #Eventually, 'DjangoModelPermissions' may be good?
#    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',), I set this in the viewSet instead
#    'PAGINATE_BY': 10, Leave default as get all
    'PAGINATE_BY_PARAM': 'page_size',
}

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geodjango',
        'USER': env['VIP_POSTGRESQL_USER'],
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

###STATICFILES_DIRS = [os.path.join(env['VIP_PYTHON_DIR'], 'lib', 'site-packages', '']
STATICFILES_DIRS = [env['VIP_DJANGO_STATIC_COMMON']]

STATIC_URL = '/'+env['VIP_DJANGO_STATIC_URL_PATH']+'/';
STATIC_ROOT = env['VIP_DJANGO_STATIC_ROOT'];
MEDIA_ROOT = env['VIP_DJANGO_MEDIA_ROOT'];

TEMPLATE_DIRS = [path.join(BASE_DIR, 'templates')]

LOGIN_REQUIRED_URLS = (r'/(.*)$',)

LOGIN_REQUIRED_URLS_EXCEPTIONS = (
  r'/login.html(.*)$',
  r'/admin(.*)$', #Admin already does its own thing, leave it alone, even though I don't have to
  r'/login(.*)$',
  r'/logout(.*)$',
)

LOGIN_URL = '/login'