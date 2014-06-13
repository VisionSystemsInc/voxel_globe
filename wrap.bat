@echo off
setlocal
%~d0
cd %~dp0

call %~dp0\np2r.bat 

if "%1"=="start_httpd" (
  httpd -f %HTTPD_CONF% > %LOG_DIR%/httpd_out.txt 2> %LOG_DIR%/httpd_err.txt
) else if "%1"=="start_celery" (
  cd %PROCESSOR_DIR%
  celery worker -A tasks --logfile=%LOG_DIR%/celery_log.txt --loglevel=INFO > %LOG_DIR%/celery_out.txt 2> %LOG_DIR%/celery_err.txt
) else if "%1"=="start_rabbitmq" (
  set HOMEDRIVE=%RABBITMQ_BASE_DRIVE%
  set HOMEPATH=%RABBITMQ_BASE_PATH%
  rabbitmq-server  > %LOG_DIR%/rabbitmq_out.txt 2> %LOG_DIR%/rabbitmq_err.txt
) else if "%1"=="start_postgresql" (
  postgres -D %DATABASE_DIR% -p %DATABASE_PORT% > %LOG_DIR%/postgresql_out.txt 2> %LOG_DIR%/postgresql_err.txt
) else if "%1"=="start_flower" (
  flower > %LOG_DIR%/flower_out.txt 2> %LOG_DIR%/flower_err.txt
) else %INSTALL_DIR%/wrap.bat %*

