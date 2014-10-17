REM Common file for windows and Linux. Keep it simple!
REM 1) No commands other than set
REM 2) No complicated expansions
REM 3) No " quotes, windows doesn't need them
REM 4) Used ; only when separating paths, because in linux it'll become :

REM ### Basic Settings ###
set VIP_PROJECT_NAME=npr
set VIP_DAEMON_GROUP=npr
set VIP_BUILD=%VIP_OS%_%VIP_ARCH%
set VIP_EMAIL=andrew.neff@vsi-ri.com
set VIP_AUTOSTART=0
set VIP_SERVICES=postgresql rabbitmq celeryd flower httpd notebook
REM Do I want to automatically start services on boot?

REM Debug flags
set VIP_DEBUG=1
REM This flags should ONLY be used in the following lines. Please create a new
REM Debug flag everytime you need it. VIP_DEBUG is just an easy way to disable
REM or enable them all at once.
set VIP_DJANGO_DEBUG=%VIP_DEBUG%
set VIP_DJANGO_TEMPLATE_DEBUG=%VIP_DEBUG%
set VIP_CELERY_AUTORELOAD=%VIP_DEBUG%
set VIP_HTTPD_DEBUG_INDEXES=%VIP_DEBUG%

set VIP_INITIALIZE_DATABASE_CONFIRM=1

REM ### DIR Settings ###
set VIP_CONF_DIR=%VIP_PROJECT_ROOT%/conf
set VIP_LOG_DIR=%VIP_PROJECT_ROOT%/logs
set VIP_LOCK_DIR=%VIP_LOCALSTATEDIR%/lock/subsys
REM Currently only Linux even uses the lock dir
set VIP_DATABASE_DIR=%VIP_PROJECT_ROOT%/data

REM ### Vxl Settings ###
set VIP_VXL_DIR=%VIP_PROJECT_ROOT%/vxl
set VIP_CMAKE=cmake
REM set VIP_CMAKE_PLATFORM=Visual Studio 11
REM For example:
REM set VIP_VXL_CMAKE_OPTIONS='"-D", "var:type=value"'

REM ### Python settings ###
set PYTHONSTARTUP=%VIP_CONF_DIR%/pythonrc.py
set VIP_NOTEBOOK_PORT=8888
set VIP_NOTEBOOK_IP=0.0.0.0
set VIP_NOTEBOOK_USER=%USERNAME%
set VIP_NOTEBOOK_LOG_DIR=%VIP_LOG_DIR%/notebook
set VIP_NOTEBOOK_PID_DIR=%VIP_PID_DIR%/notebook
set VIP_NOTEBOOK_LOCK_DIR=%VIP_LOCK_DIR%/notebook

REM ### Django settings
set VIP_DJANGO_PROJECT=%VIP_PROJECT_ROOT%/web
set VIP_DJANGO_SITE=%VIP_DJANGO_PROJECT%/nga
set VIP_DJANGO_STATIC_ROOT=%VIP_DJANGO_PROJECT%/static_deploy
set VIP_DJANGO_SETTINGS_MODULE=nga.settings
set VIP_DJANGO_STATIC_URL_PATH=static
set VIP_DJANGO_MEDIA_ROOT=%VIP_DJANGO_PROJECT%/media_root
REM Note: Since environment variables are process-wide, this doesn’t work when you
REM run multiple Django sites in the same process. This happens with mod_wsgi.
REM To avoid this problem, use mod_wsgi’s daemon mode with each site in its own daemon
REM process, or override the value from the environment by enforcing 
REM os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings" in your wsgi.py.

set VIP_DJANGO_REGRESSION_APP=world
set VIP_DJANGO_REGRESSION_SHAPEFILE=%VIP_DATABASE_DIR%/world_borders/TM_WORLD_BORDERS-0.3.shp
set VIP_DJANGO_USER=npr
set VIP_DJANGO_PASSWD=%VIP_PROJECT_ROOT%/shadow/django

REM ### POSTGRESQL Settings ###
REM For connecting
set VIP_POSTGRESQL_HOST=localhost
set VIP_POSTGRESQL_PORT=5432
REM set VIP_POSTGRESQL_USER=npr_postgresql REM AEN Obviously I still don't understand this still
set VIP_POSTGRESQL_USER=postgresql
set VIP_POSTGRESQL_PASSWORD=vsi
set VIP_POSTGRESQL_DATABASE_NAME=geodjango
set VIP_POSTGRESQL_CREDENTIALS=-U %VIP_POSTGRESQL_USER% -h %VIP_POSTGRESQL_HOST% -p %VIP_POSTGRESQL_PORT%
set VIP_POSTGRESQL_SERVER_CREDENTIALS=-h %VIP_POSTGRESQL_HOST% -p %VIP_POSTGRESQL_PORT%

REM For setup
set VIP_POSTGRESQL_DATABASE=%VIP_DATABASE_DIR%/postgresql
set VIP_POSTGRESQL_PID_DIR=%VIP_PID_DIR%/postgresql
set VIP_POSTGRESQL_LOG_DIR=%VIP_LOG_DIR%/postgresql
set VIP_POSTGRESQL_LOG=%VIP_POSTGRESQL_LOG_DIR%/pg.log
set VIP_POSTGRESQL_LOCK_DIR=%VIP_LOCK_DIR%/postgresql
set VIP_POSTGRESQL_DIR=%VIP_INSTALL_DIR%/postgresql

set VIP_POSTGRESQL_ENCODING=UTF-8
set VIP_POSTGRESQL_AUTH=trust
REM This is ok for current dev, but will soon be md5, unless for some reason YEARS down the road,
REM db-namespace is needed, in which case we will switch over to ssl connections only with password auth

REM ### Celery Settings ###
set VIP_CELERY_DEFAULT_NODES=npr
set VIP_CELERY_DAEMON_USER=npr_celery
set VIP_CELERY_PROCESSORS=%VIP_PROJECT_ROOT%/processors
set VIP_CELERY_PID_DIR=%VIP_PID_DIR%/celery
set VIP_CELERY_LOG_DIR=%VIP_LOG_DIR%/celery
set VIP_CELERY_LOCK_DIR=%VIP_LOCK_DIR%/celery

set VIP_NOTEBOOK_RUN_DIR=%VIP_CELERY_PROCESSORS%

REM ##### RABITMQ Settings ##### 
set VIP_RABBITMQ_PID_DIR=%VIP_PID_DIR%/rabbitmq
set VIP_RABBITMQ_LOCK_DIR=%VIP_LOCK_DIR%/rabbitmq
set VIP_RABBITMQ_LOG_DIR=%VIP_LOG_DIR%/rabbitmq
set VIP_RABBITMQ_PID_FILE=%VIP_PID_DIR%/rabbitmq.pid

set VIP_RABBITMQ_USER=npr_rabbitmq
set VIP_RABBITMQ_MNESIA_BASE=%VIP_DATABASE_DIR%

REM ##### Image Server Settings #####
set VIP_IMAGE_SERVER_HOST=localhost
set VIP_IMAGE_SERVER_PORT=80
set VIP_IMAGE_SERVER_URL_PATH=images
  REM Where are the images served from
set VIP_IMAGE_SERVER_ROOT=%VIP_PROJECT_ROOT%/images
  REM Where are the images physically/virtually?

set VIP_IMAGE_SERVER_AUTHORITY=%VIP_IMAGE_SERVER_HOST%:%VIP_IMAGE_SERVER_PORT%

REM ##### Apache HTTPD Settings ##### 
set VIP_HTTPD_CONF=%VIP_CONF_DIR%/httpd.conf
set VIP_HTTPD_PORT=80
set VIP_HTTPD_SSL_PORT=443
set VIP_HTTPD_DAEMON_USER=npr_httpd
set VIP_HTTPD_DAEMON_GROUP=%VIP_DAEMON_GROUP%
set VIP_HTTPD_PID_DIR=%VIP_PID_DIR%/httpd
set VIP_HTTPD_LOG_DIR=%VIP_LOG_DIR%/httpd
set VIP_HTTPD_LOCK_DIR=%VIP_LOCK_DIR%/httpd
set VIP_HTTPD_LOG_LEVEL=info
set VIP_HTTPD_DEPLOY_ON_START=1
set VIP_HTTPD_SERVER_NAME=www.vsi-ri.com

set VIP_WSGI_PYTHON_DIR=%VIP_PYTHON_DIR%
REM THIS was annoying, WSGI auto adds bin in linux, SO my roam isn't used, however
REM APACHE is started in my environment, so I'm sure this is why everything is working?
set VIP_WSGI_PYTHON_PATH=%VIP_DJANGO_PROJECT%;%VIP_CELERY_PROCESSORS%
REM For the initial wsgi.py file and all Celery processors
set VIP_WSGI_SCRIPT_ALIAS=%VIP_DJANGO_SITE%/wsgi.py

set VIP_UTIL_DIR=%VIP_INSTALL_DIR%/utils

REM *********** NON-VIP Section. There can affect ANYTHING ***********
REM These parameters are not protected by the VIP Prefix, and thus
REM Affect many application, but hopefully in a good way :)

set DJANGO_SETTINGS_MODULE=%VIP_DJANGO_SETTINGS_MODULE%

REM I don't know if this is actually used, but it is mentioned in the Geodjango tutorial
set PROJ_LIB=%VIP_DJANGO_PROJ_LIB%
set GDAL_DATA=%VIP_DJANGO_GDAL_DATA%
set POSTGIS_ENABLE_OUTDB_RASTERS=1
set POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL
set POSTGIS_GDAL_ENABLED_DRIVERS=GTiff PNG JPEG GIF XYZ
