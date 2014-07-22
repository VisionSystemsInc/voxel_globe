"""
Django settings for nga project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#if 'LIBDIR' in os.environ:
#  GEOS_LIBRARY_PATH=os.path.join(os.environ['LIBDIR'],'libgeos_c.so')
#Really only needed for Linux, I think
#GDAL_LIBRARY_PATH='/opt/users/andy/projects/ngap2/code/external/bin_Linux_x86_64/lib/libgdal.so'

GEOS_LIBRARY_PATH=os.environ['NPR_DJANGO_GEOS_LIBRARY_PATH'];
GDAL_LIBRARY_PATH=os.environ['NPR_DJANGO_GDAL_LIBRARY_PATH'];

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20hiyp8-=0+oan+sa(r$xz#j83jr5*13*(j_(a)9q234cynf+&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'meta',
    'world'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nga.urls'

WSGI_APPLICATION = 'nga.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'geodjango',
        'USER': os.environ['NPR_POSTGRESQL_USER'],
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = os.environ['NPR_DJANGO_STATIC_DIR'];
STATIC_ROOT = os.environ['NPR_DJANGO_STATIC_ROOT'];
MEDIA_ROOT = os.environ['NPR_DJANGO_MEDIA_ROOT'];

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
