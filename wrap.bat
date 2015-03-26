@echo off
setlocal enabledelayedexpansion

call %~dp0vip.bat %*

if "%VIP_NARG%" == "0" (
  %~d0
  REM swtich to that drive (c: or other)
  cd %~dp0
  REM cd script dir
)

call %VIP_INSTALL_DIR%/wrap.bat %*

REM set RAB_TARGET=%1
REM if "%RAB_TARGET:~0,8%"=="rabbitmq" set WRAP_IS_RABBITMQ=1
REM if "%1"=="start_rabbitmq" set WRAP_IS_RABBITMQ=1
REM if "%WRAP_IS_RABBITMQ%"=="1" (
  REM if not exist %VIP_RABBITMQ_LOG_DIR:/=\% mkdir %VIP_RABBITMQ_LOG_DIR:/=\%
  REM set RABBITMQ_BASE=%VIP_PROJECT_ROOT%
  REM set RABBITMQ_LOG_BASE=%VIP_RABBITMQ_LOG_DIR%
  REM set RABBITMQ_MNESIA_BASE=%VIP_RABBITMQ_MNESIA_BASE%
  REM set HOMEDRIVE=%VIP_RABBITMQ_BASE_DRIVE%
  REM set HOMEPATH=%VIP_RABBITMQ_BASE_PATH%
  REM set RABBITMQ_PID_FILE=%VIP_RABBITMQ_PID_FILE%
  REM set ERLANG_HOME=%VIP_RABBITMQ_ERLANG_HOME%
REM )
REM REM Delete unused vars
REM set RAB_TARGET=
REM set WRAP_IS_RABBITMQ=

REM if "%1"=="start_httpd" (
  REM set PIDFILE=%VIP_HTTPD_PID_DIR%/httpd.pid
  REM if "%VIP_HTTPD_DEPLOY_ON_START%" == "1" call %VIP_DJANGO_PROJECT%/deploy.bat > %VIP_HTTPD_LOG_DIR%/deploy_out.log 2> %VIP_HTTPD_LOG_DIR%/deploy_err.log
  REM if "%VIP_HTTPD_DEBUG_INDEXES%" == "1" set HTTPD_OPTIONS=%HTTPD_OPTIONS% -Ddebug_indexes
  REM if not exist %VIP_HTTPD_LOG_DIR:/=\% mkdir %VIP_HTTPD_LOG_DIR:/=\%
  REM httpd !HTTPD_OPTIONS! -f %VIP_HTTPD_CONF% > %VIP_HTTPD_LOG_DIR%/httpd_out.log 2> %VIP_HTTPD_LOG_DIR%/httpd_err.log
REM ) else if "%1"=="start_celeryd" (
  REM celery worker -A %VIP_CELERY_APP% --logfile=%VIP_LOG_DIR%/celery_log.log --loglevel=%VIP_CELERYD_LOG_LEVEL% > %VIP_LOG_DIR%/celery_out.log 2> %VIP_LOG_DIR%/celery_err.log
REM ) else if "%1"=="start_rabbitmq" (
  REM rabbitmq-server > %VIP_RABBITMQ_LOG_DIR%/rabbitmq_out.log 2> %VIP_RABBITMQ_LOG_DIR%/rabbitmq_err.log
REM ) else if "%1"=="start_postgresql" (
  REM postgres -D %VIP_POSTGRESQL_DATABASE% %VIP_POSTGRESQL_SERVER_CREDENTIALS% > %VIP_LOG_DIR%/postgresql_out.log 2> %VIP_LOG_DIR%/postgresql_err.log
REM ) else if "%1"=="start_flower" (
  REM flower --address=0.0.0.0 --port=%VIP_FLOWER_PORT%  > %VIP_LOG_DIR%/flower_out.log 2> %VIP_LOG_DIR%/flower_err.log
REM ) else if "%1"=="start_notebook" (
  REM psexec -i -u "%VIP_DAEMON_USER%" %VIP_PYTHON_DIR%/Scripts/ipython notebook --notebook-dir=%VIP_NOTEBOOK_RUN_DIR% --no-browser --port=%VIP_NOTEBOOK_PORT% --ip=%VIP_NOTEBOOK_IP% --matplotlib=inline --profile-dir=%VIP_NOTEBOOK_PROFILE_DIR% 
REM REM > %VIP_LOG_DIR%/notebook_out.log 2> %VIP_LOG_DIR%/notebook_err.log
REM ) else (
  REM %VIP_INSTALL_DIR%/wrap.bat %*
REM )

endlocal
