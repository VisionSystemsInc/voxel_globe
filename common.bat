REM Common file for windows and Linux. Keep it simple!
REM 1) No commands other than set
REM 2) No complicated expansions
REM 3) No " quotes?
REM 4) Used ; only when separating paths, because in linux it'll become :

set VSI_PROJECT_NAME=npr

set NPR_DAEMON_GROUP=npr

set NPR_BUILD=%OS%_%ARCH%

set NPR_CONF_DIR=%NPR_PROJECT_ROOT%/conf
set NPR_LOG_DIR=%NPR_PROJECT_ROOT%/logs

set NPR_DATABASE_DIR=%NPR_PROJECT_ROOT%/data

set NPR_EMAIL=andrew.neff@vsi-ri.com
set NPR_AUTOSTART=0

set PYTHONSTARTUP=%NPR_CONF_DIR%/pythonrc.py
set NPR_NOTEBOOK_PORT=8888
set NPR_NOTEBOOK_USER=%USERNAME%

set NPR_NOTEBOOK_LOG_DIR=%NPR_LOG_DIR%/notebook
set NPR_NOTEBOOK_PID_DIR=%NPR_PID_DIR%/notebook
set NPR_NOTEBOOK_LOCK_DIR=%NPR_LOCK_DIR%/notebook

set NPR_DJANGO_PROJECT=%NPR_PROJECT_ROOT%/web
set NPR_DJANGO_SITE=%NPR_DJANGO_PROJECT%/nga
set NPR_DJANGO_STATIC_ROOT=%NPR_DJANGO_PROJECT%/static_deploy
set NPR_DJANGO_SETTINGS_MODULE=nga.settings
set NPR_DJANGO_STATIC_DIR=/static/
set NPR_DJANGO_MEDIA_ROOT=%NPR_DJANGO_PROJECT%/media_root
REM Note: Since environment variables are process-wide, this doesn’t work when you
REM run multiple Django sites in the same process. This happens with mod_wsgi.
REM To avoid this problem, use mod_wsgi’s daemon mode with each site in its own daemon
REM process, or override the value from the environment by enforcing 
REM os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings" in your wsgi.py.

set NPR_DJANGO_REGRESSION_APP=world
set NPR_DJANGO_REGRESSION_SHAPEFILE=%NPR_DATABASE_DIR%/world_borders/TM_WORLD_BORDERS-0.3.shp

REM AENset NPR_DJANGO_USER=npr
REM AENset NPR_DJANGO_PASSWD=%NPR_PROJECT_ROOT%/shadow/django

REM ##### POSTGRESQL var #####
REM For connecting
set NPR_POSTGRESQL_HOST=localhost
set NPR_POSTGRESQL_PORT=5432
REM set NPR_POSTGRESQL_USER=npr_postgresql REM AEN Obviously I still don't understand this still
set NPR_POSTGRESQL_USER=postgresql
set NPR_POSTGRESQL_PASSWORD=vsi
set NPR_POSTGRESQL_DATABASE_NAME=geodjango
set NPR_POSTGRESQL_CREDENTIALS=-U %NPR_POSTGRESQL_USER% -h %NPR_POSTGRESQL_HOST% -p %NPR_POSTGRESQL_PORT%
set NPR_POSTGRESQL_SERVER_CREDENTIALS=-h %NPR_POSTGRESQL_HOST% -p %NPR_POSTGRESQL_PORT%

REM For setup
set NPR_POSTGRESQL_DATABASE=%NPR_DATABASE_DIR%/postgresql
set NPR_POSTGRESQL_PID_DIR=%NPR_PID_DIR%/postgresql
set NPR_POSTGRESQL_LOG_DIR=%NPR_LOG_DIR%/postgresql
set NPR_POSTGRESQL_LOG=%NPR_POSTGRESQL_LOG_DIR%/pg.log
set NPR_POSTGRESQL_LOCK_DIR=%NPR_LOCK_DIR%/postgresql

set NPR_POSTGRESQL_DIR=%NPR_INSTALL_DIR%/postgresql

set NPR_POSTGRESQL_ENCODING=UTF-8
set NPR_POSTGRESQL_AUTH=trust


set NPR_CELERY_DEFAULT_NODES=npr
set NPR_CELERY_DAEMON_USER=npr_celery
set NPR_CELERY_PROCESSORS=%NPR_PROJECT_ROOT%/processors
set NPR_CELERY_PID_DIR=%NPR_PID_DIR%/celery
set NPR_CELERY_LOG_DIR=%NPR_LOG_DIR%/celery
set NPR_CELERY_LOCK_DIR=%NPR_LOCK_DIR%/celery

REM ##### RABITMQ vars ##### 
set NPR_RABBITMQ_SERVER_PID_DIR=%NPR_PID_DIR%/rabbitmq-server
set NPR_RABBITMQ_SERVER_LOCK_DIR=%NPR_LOCK_DIR%/rabbitmq-server
set NPR_RABBITMQ_SERVER_LOG_DIR=%NPR_LOG_DIR%/rabbitmq-server
set NPR_RABBITMQ_SERVER_PID_FILE=%NPR_PID_DIR%/rabbitmq_server.pid

set NPR_RABBITMQ_SERVER_USER=npr_rabbitmq
set NPR_RABBITMQ_SERVER_MNESIA_BASE=%NPR_DATABASE_DIR%

REM ##### Apache HTTPD vars ##### 
set NPR_HTTPD_CONF=%NPR_CONF_DIR%/httpd.conf
set NPR_HTTPD_PORT=80
set NPR_HTTPD_SSL_PORT=443
set NPR_HTTPD_DAEMON_USER=npr_httpd
set NPR_HTTPD_DAEMON_GROUP=%NPR_DAEMON_GROUP%
set NPR_HTTPD_UNPRIVLEDGED_PORT=8080
set NPR_HTTPD_UNPRIVLEDGED_SSL_PORT=8443
set NPR_HTTPD_PID_DIR=%NPR_PID_DIR%/httpd
set NPR_HTTPD_LOG_DIR=%NPR_LOG_DIR%/httpd
set NPR_HTTPD_LOCK_DIR=%NPR_LOCK_DIR%/httpd
set NPR_HTTPD_LOG_LEVEL=info

set NPR_WSGI_PYTHON_DIR=%NPR_PYTHON_DIR%
set NPR_WSGI_PYTHON_PATH=%NPR_DJANGO_PROJECT%;%NPR_CELERY_PROCESSORS%
REM For the initial wsgi.py file and all Celery processors
set NPR_WSGI_SCRIPT_ALIAS=%NPR_DJANGO_SITE%/wsgi.py

set NPR_UTIL_DIR=%NPR_INSTALL_DIR%/utils

REM *********** NON-NPR Section. There can affect ANYTHING ***********
REM These parameters are not protected by the NPR Prefix, and thus
REM Affect many application, but hopefully in a good way :)


set DJANGO_SETTINGS_MODULE=%NPR_DJANGO_SETTINGS_MODULE%

set PROJ_LIB=%NPR_DJANGO_PROJ_LIB%
set GDAL_DATA=%NPR_DJANGO_GDAL_DATA%
set POSTGIS_ENABLE_OUTDB_RASTERS=1
set POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL
set POSTGIS_GDAL_ENABLED_DRIVERS=GTiff PNG JPEG GIF XYZ
