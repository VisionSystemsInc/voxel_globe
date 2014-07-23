@echo off
setlocal

call %~dp0\np2r.bat %*

if "%argC%" == "0" (
  %~d0
  cd %~dp0
)

if "%1"=="start_httpd" (
  set PIDFILE=%NPR_HTTPD_PID_DIR%/httpd.pid
  httpd -f %NPR_HTTPD_CONF% > %NPR_LOG_DIR%/httpd_out.log 2> %NPR_LOG_DIR%/httpd_err.log
) else if "%1"=="start_celery" (
 
  :waitfordatabase
  pg_isready %NPR_POSTGRESQL_CREDENTIALS%
  if "%errorlevel%" NEQ "0" (
    echo "Waiting for database to come up..."
    timeout /T 1 /NOBREAK
	goto waitfordatabase
  )

  celery worker -A tasks --logfile=%NPR_LOG_DIR%/celery_log.log --loglevel=INFO > %NPR_LOG_DIR%/celery_out.log 2> %NPR_LOG_DIR%/celery_err.log
) else if "%1"=="start_rabbitmq" (
  set RABBITMQ_BASE=%NPR_PROJECT_ROOT%
  set RABBITMQ_LOG_BASE=%NPR_RABBITMQ_SERVER_LOG_DIR%
  set RABBITMQ_MNESIA_BASE=%NPR_RABBITMQ_SERVER_MNESIA_BASE%
  set HOMEDRIVE=%NPR_RABBITMQ_BASE_DRIVE%
  set HOMEPATH=%NPR_RABBITMQ_BASE_PATH%
  set RABBITMQ_PID_FILE=%NPR_RABBITMQ_SERVER_PID_FILE%
  set ERLANG_HOME=%NPR_RABBITMQ_ERLANG_HOME%
  rabbitmq-server  > %NPR_LOG_DIR%/rabbitmq_out.log 2> %NPR_LOG_DIR%/rabbitmq_err.log
) else if "%1"=="start_postgresql" (
  postgres -D %NPR_POSTGRESQL_DATABASE% %NPR_POSTGRESQL_SERVER_CREDENTIALS% > %NPR_LOG_DIR%/postgresql_out.log 2> %NPR_LOG_DIR%/postgresql_err.log
) else if "%1"=="start_flower" (
  flower > %NPR_LOG_DIR%/flower_out.log 2> %NPR_LOG_DIR%/flower_err.log
) else if "%1"=="start_notebook" (
  ipython notebook --no-browser --port=%NPR_NOTEBOOK_PORT% > %NPR_LOG_DIR%/notebook_out.log 2> %NPR_LOG_DIR%/notebook_err.log
) else %NPR_INSTALL_DIR%/wrap.bat %*

endlocal