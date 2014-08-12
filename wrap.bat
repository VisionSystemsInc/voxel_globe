@echo off
setlocal enabledelayedexpansion

call %~dp0vip.bat %*

if "%VIP_NARG%" == "0" (
  %~d0
  cd %~dp0
)

if "%1"=="start_httpd" (
  set PIDFILE=%VIP_HTTPD_PID_DIR%/httpd.pid
  if "%VIP_HTTPD_DEBUG_INDEXES%" == "1" set HTTPD_OPTIONS=%HTTPD_OPTIONS% -Ddebug_indexes
  if not exist %VIP_HTTPD_LOG_DIR:/=\% mkdir %VIP_HTTPD_LOG_DIR:/=\%
  httpd !HTTPD_OPTIONS! -f %VIP_HTTPD_CONF% > %VIP_HTTPD_LOG_DIR%/httpd_out.log 2> %VIP_HTTPD_LOG_DIR%/httpd_err.log
) else if "%1"=="start_celeryd" (
 
  :waitfordatabase
  pg_isready %VIP_POSTGRESQL_CREDENTIALS%
  if "%errorlevel%" NEQ "0" (
    echo "Waiting for database to come up..."
    timeout /T 1 /NOBREAK
	goto waitfordatabase
  )

  celery worker -A tasks --logfile=%VIP_LOG_DIR%/celery_log.log --loglevel=INFO > %VIP_LOG_DIR%/celery_out.log 2> %VIP_LOG_DIR%/celery_err.log
) else if "%1"=="start_rabbitmq" (
  if not exist %VIP_RABBITMQ_LOG_DIR:/=\% mkdir %VIP_RABBITMQ_LOG_DIR:/=\%
  set RABBITMQ_BASE=%VIP_PROJECT_ROOT%
  set RABBITMQ_LOG_BASE=%VIP_RABBITMQ_LOG_DIR%
  set RABBITMQ_MNESIA_BASE=%VIP_RABBITMQ_MNESIA_BASE%
  set HOMEDRIVE=%VIP_RABBITMQ_BASE_DRIVE%
  set HOMEPATH=%VIP_RABBITMQ_BASE_PATH%
  set RABBITMQ_PID_FILE=%VIP_RABBITMQ_PID_FILE%
  set ERLANG_HOME=%VIP_RABBITMQ_ERLANG_HOME%
  rabbitmq-server > %VIP_RABBITMQ_LOG_DIR%/rabbitmq_out.log 2> %VIP_RABBITMQ_LOG_DIR%/rabbitmq_err.log
) else if "%1"=="start_postgresql" (
  postgres -D %VIP_POSTGRESQL_DATABASE% %VIP_POSTGRESQL_SERVER_CREDENTIALS% > %VIP_LOG_DIR%/postgresql_out.log 2> %VIP_LOG_DIR%/postgresql_err.log
) else if "%1"=="start_flower" (
  flower > %VIP_LOG_DIR%/flower_out.log 2> %VIP_LOG_DIR%/flower_err.log
) else if "%1"=="start_notebook" (
  ipython notebook --no-browser --port=%VIP_NOTEBOOK_PORT% --ip=%VIP_NOTEBOOK_IP% > %VIP_LOG_DIR%/notebook_out.log 2> %VIP_LOG_DIR%/notebook_err.log
) else %VIP_INSTALL_DIR%/wrap.bat %*

endlocal
