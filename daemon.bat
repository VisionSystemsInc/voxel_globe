@echo off

set SERVICES=httpd flower celery rabbitmq postgresql notebook

setlocal

set argC=0
for %%x in (%*) do Set /A argC+=1

if not "%argC%"=="2" (
  echo ERROR: Two arguments only
  goto usage
)

::Special case all
if /i "%1" == "all" (
  set TASKS=%SERVICES%
  goto valid_service_name
)
::See if any of the names match
for %%i in (%SERVICES%) do (
  if /i "%1" == "%%i" (
    set TASKS=%1
    goto valid_service_name
  )
)
goto usage

:valid_service_name
set NEXT=usage
for %%i in (start stop restart status) do (
  if /i "%%i"=="%2" set NEXT=%2
)

if "%NEXT%"=="usage" goto usage
::Skip elevate because there is no reason

:check_elevated
net session >nul 2>&1
if not %errorLevel% == 0 (
  echo Elevated permissions...
  ECHO Set UAC = CreateObject^("Shell.Application"^) > "%~dp0\OEgetPrivileges.vbs" 
  ECHO UAC.ShellExecute "%~f0", "%*", "", "runas", 1 >> "%~dp0\OEgetPrivileges.vbs" 
  "%~dp0\OEgetPrivileges.vbs" 
  exit /B 1
)
del %~dp0\OEgetPrivileges.vbs > NUL 2>&1

goto %NEXT%
goto usage
::Just in case something went REALLY wrong?!

:start
for %%t in (%TASKS%) do schtasks /run /TN %%t_daemon
goto done

:stop
for %%t in (%TASKS%) do (
  schtasks /end /TN %%t_daemon
  if /i "%%t"=="rabbitmq" taskkill /im epmd.exe /f
  REM if "%%t"=="rabbitmq" %EMPD_IM% -kill
)
goto done

:restart
for %%t in (%TASKS%) do schtasks /end /TN %%t_daemon
for %%t in (%TASKS%) do schtasks /run /TN %%t_daemon
goto done

:status
for %%t in (%TASKS%) do schtasks /query /TN %%t_daemon
goto done

:usage
echo Usages: %0 {service_name} [start^|stop^|restart^|status]
echo   where service_name can be [%SERVICES%]

:done
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause