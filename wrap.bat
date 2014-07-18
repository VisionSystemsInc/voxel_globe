@echo off
setlocal

call %~dp0\np2r.bat %*

if "%argC%" == "0" (
  %~d0
  cd %~dp0
)

if "%1"=="start_httpd" (
  set PIDFILE=%NPR_HTTPD_PID_DIR%/httpd.pid
  httpd -f %NPR_HTTPD_CONF% > %NPR_LOG_DIR%/httpd_out.txt 2> %NPR_LOG_DIR%/httpd_err.txt
) else if "%1"=="start_celery" (
  REM cd %NPR_CELERY_PROCESSORS%
  if "%PYTHONPATH%" == "%^PYTHONPATH%" (
    set PYTHONPATH=%PYTHONPATH%;%NPR_CELERY_PROCESSORS%;%NPR_DJANGO_PROJECT%
  ) else (
	set PYTHONPATH=%NPR_CELERY_PROCESSORS%;%NPR_DJANGO_PROJECT%
  )

  set PROJ_LIB=%PROJ_LIB%
  set GDAL_DATA=%GDAL_DATA%
  
  set DJANGO_SETTINGS_MODULE=%NPR_DJANGO_SETTINGS_MODULE%
  
  pg_isready -p %NPR_POSTGRESQL_PORT%
  REM This is NOT ENOUGH, I need a while loop waiting until true or a max, TIMEOUT DOENS'T WORK!

  celery worker -A tasks --logfile=%NPR_LOG_DIR%/celery_log.txt --loglevel=INFO > %NPR_LOG_DIR%/celery_out.txt 2> %NPR_LOG_DIR%/celery_err.txt
) else if "%1"=="start_rabbitmq" (
  set RABBITMQ_BASE=%NPR_PROJECT_ROOT%
  set RABBITMQ_LOG_BASE=%NPR_RABBITMQ_SERVER_LOG_DIR%
  set RABBITMQ_MNESIA_BASE=%NPR_RABBITMQ_SERVER_MNESIA_BASE%
  set HOMEDRIVE=%NPR_RABBITMQ_BASE_DRIVE%
  set HOMEPATH=%NPR_RABBITMQ_BASE_PATH%
  set RABBITMQ_PID_FILE=%NPR_RABBITMQ_SERVER_PID_FILE%
  set ERLANG_HOME=%NPR_RABBITMQ_ERLANG_HOME%
  rabbitmq-server  > %NPR_LOG_DIR%/rabbitmq_out.txt 2> %NPR_LOG_DIR%/rabbitmq_err.txt
) else if "%1"=="start_postgresql" (
  postgres -D %NPR_POSTGRESQL_DATABASE% -p %NPR_POSTGRESQL_PORT% > %NPR_LOG_DIR%/postgresql_out.txt 2> %NPR_LOG_DIR%/postgresql_err.txt
) else if "%1"=="start_flower" (
  flower > %NPR_LOG_DIR%/flower_out.txt 2> %NPR_LOG_DIR%/flower_err.txt
) else if "%1"=="start_notebook" (
  ipython notebook --no-browser --port=%NPR_NOTEBOOK_PORT% > %NPR_LOG_DIR%/notebook_out.txt 2> %NPR_LOG_DIR%/notebook_err.txt
) else %NPR_INSTALL_DIR%/wrap.bat %*
