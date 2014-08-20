@echo off

setlocal enabledelayedexpansion

call %~dp0vip.bat

set VIP_NARG=0
for %%x in (%*) do Set /A VIP_NARG+=1

if not "%VIP_NARG%"=="2" (
  echo ERROR: Two arguments only
  goto usage
)

::Special case all
if /i "%1" == "all" (
  if /i "%2" == "stop" (
  REM Stop in reverse order, and NO, GOOGLE DID NOT HELP HERE! This is ALL AEN!
	set TEMPTASKS=%VIP_SERVICES%

    set NUMT=0
    for %%x in (!TEMPTASKS!) do set /A NUMT+=1

    for /L %%x in (!NUMT!, -1, 1) do (
      set COUNTT=0
      for %%y in (!TEMPTASKS!) do (
        set /A COUNTT+=1
	    if "!COUNTT!"=="%%x" set TASKS=!TASKS! %%y
      )
    )
  ) else (
    set TASKS=%VIP_SERVICES%
  )
  goto valid_service_name
)
::See if any of the names match
for %%i in (%VIP_SERVICES%) do (
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
for %%t in (%TASKS%) do schtasks /run /TN %%t_%VIP_DAEMON_POSTFIX%
goto done

:stop
for %%t in (%TASKS%) do (
  schtasks /end /TN %%t_%VIP_DAEMON_POSTFIX%
  if /i "%%t"=="rabbitmq" taskkill /im %VIP_RABBITMQ_DAEMON% /f
  if /i "%%t"=="postgresql" (
    pg_isready %VIP_POSTGRESQL_CREDENTIALS% > NUL
    if not errorlevel 1 (
      echo Stray postgresql detected, cleaning up
      pg_ctl stop -D %VIP_POSTGRESQL_DATABASE% -m fast 2>&1 >> %VIP_POSTGRESQL_LOG_DIR%/postgresql_stop_stray.log
    )
  )
)
goto done

:restart
for %%t in (%TASKS%) do schtasks /end /TN %%t_%VIP_DAEMON_POSTFIX%
for %%t in (%TASKS%) do schtasks /run /TN %%t_%VIP_DAEMON_POSTFIX%
goto done

:status
for %%t in (%TASKS%) do schtasks /query /TN %%t_%VIP_DAEMON_POSTFIX%
goto done

:usage
echo Usages: %0 {service_name} [start^|stop^|restart^|status]
echo   where service_name can be [%VIP_SERVICES%]

:done
echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

endlocal
