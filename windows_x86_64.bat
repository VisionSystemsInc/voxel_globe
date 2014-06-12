@echo off

%~d0
cd %~dp0

call %~dp0external/bin_Windows_x86_64/env.bat 
REM STUPID BATCH LIMITATAIONS!!! > : O

if "%1"=="start_httpd" (
  httpd -f %APACHE_CONF%
) else if "%1"=="start_celery" (
  cd %PROCESSOR_DIR%
  celery worker -A tasks --logfile=%LOG_DIR%/celery_log.txt --loglevel=INFO > %LOG_DIR%/celery_out.txt 2> %LOG_DIR%/celery_err.txt
) else if "%1"=="start_rabbitmq" (
  set HOMEDRIVE=%CONF_DRIVE%
  set HOMEPATH=%CONF_PATH%
  rabbitmq-server  > %LOG_DIR%/rabbitmq_out.txt 2> %LOG_DIR%/rabbitmq_err.txt
) else if "%1"=="start_postgresql" (
  postgresql > %LOG_DIR%/postgresql_out.txt 2> %LOG_DIR%/postgresql_err.txt
) else if "%1"=="start_flower" (
  flower > %LOG_DIR%/flower_out.txt 2> %LOG_DIR%/flower_err.txt
) else %*

