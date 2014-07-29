@echo off

setlocal

call %~dp0/np2r.bat

set NPR_NARG=0
for %%x in (%*) do Set /A NPR_NARG+=1

if not "%NPR_NARG%"=="2" (
  echo ERROR: Two arguments only
  goto usage
)

::Special case all
if /i "%1" == "all" (
  set TASKS=%NPR_SERVICES%
  goto valid_service_name
)
::See if any of the names match
for %%i in (%NPR_SERVICES%) do (
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
  if "%attemptElevate%" NEQ "1" (
    set attemptElevate=1
    echo Elevated permissions...
    ECHO Set UAC = CreateObject^("Shell.Application"^) > "%~dp0\OEgetPrivileges.vbs" 
    ECHO UAC.ShellExecute "%~f0", "%*", "", "runas", 1 >> "%~dp0\OEgetPrivileges.vbs" 
    "%~dp0\OEgetPrivileges.vbs" 
    exit /B 1
  ) else (
    echo ERROR: Elevation of permissinos FAILED. I will attempt to run the command anyway ^
but it will probably fail. Please make sure you are running from an user account ^
that has the capability of elevate ^(UAC permissions^), not neccesarily an ^
admin account.
  )
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
  if /i "%%t"=="rabbitmq" taskkill /im %NPR_RABBITMQ_DAEMON% /f
  if /i "%%t"=="postgresql" (
    pg_isready %NPR_POSTGRESQL_CREDENTIALS% > NUL
	if "%errorlevel%" == "0" (
	  echo Stray postgresql detected, cleaning up
	  pg_ctl stop -D %NPR_POSTGRESQL_DATABASE% -m fast 2>1 >> %NPR_LOG_DIR%/postgresql_stop_stray.log
	)
  )
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
echo   where service_name can be [%NPR_SERVICES%]

:done
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

endlocal
