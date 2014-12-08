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
  if /i "%2" == "stop" set VIP_RESERVE_ORDER=1
  if /i "%2" == "restart" set VIP_RESERVE_ORDER=1
  if "!VIP_RESERVE_ORDER!" == "1" (
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
    set VIP_RESERVE_ORDER=
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
for %%i in (start stop restart status killall) do (
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

REM Create log directories incase they don't exist.
if not exist %VIP_POSTGRESQL_LOG_DIR:/=\% mkdir %VIP_POSTGRESQL_LOG_DIR:/=\%
if not exist %VIP_RABBITMQ_LOG_DIR:/=\% mkdir %VIP_RABBITMQ_LOG_DIR:/=\%
if not exist %VIP_CELERY_LOG_DIR:/=\% mkdir %VIP_CELERY_LOG_DIR:/=\%
if not exist %VIP_NOTEBOOK_LOG_DIR:/=\% mkdir %VIP_NOTEBOOK_LOG_DIR:/=\%
if not exist %VIP_HTTPD_LOG_DIR:/=\% mkdir %VIP_HTTPD_LOG_DIR:/=\%

goto %NEXT%
goto usage
::Just in case something went REALLY wrong?!

:start
for %%t in (%TASKS%) do (
  schtasks /run /TN %%t_%VIP_DAEMON_POSTFIX%
  
  if /i "%%t"=="postgresql" (
    for /l %%q in (1,1,10) do (
      if !VIP_POSTGRESQL_TEMP_STARTED! NEQ 1 (
        pg_isready %VIP_POSTGRESQL_CREDENTIALS% > nul
        if "!errorlevel!" NEQ "0" (
          echo Waiting for database to come up... %%q
          timeout /T 1 /NOBREAK > nul
        ) else (
          set VIP_POSTGRESQL_TEMP_STARTED=1
        )
      )
    )
    if !VIP_POSTGRESQL_TEMP_STARTED! NEQ 1 (
      echo Postgresql has failed to start. If you are continuing to see
      echo this, please contact an administrator.
    )
    set VIP_POSTGRESQL_TEMP_STARTED=
  )

  if /i "%%t"=="httpd" (
    for /l %%q in (1, 1, 5) do (
      if !VIP_HTTPD_TEMP_STARTED! NEQ 1 (
        python -c "import urllib2; exec('try:\n  urllib2.urlopen(\'http://localhost:%VIP_HTTPD_PORT%/\', timeout=10)\nexcept urllib2.HTTPError:\n  exit(0)')" > NUL 2>&1
        if "!errorlevel!"=="0" set VIP_HTTPD_TEMP_STARTED=1
        echo Waiting for httpd server to come up... %%q
        timeout /T 1 /NOBREAK > nul
      )
    )
    if !VIP_HTTPD_TEMP_STARTED! NEQ 1 (
      echo Either httpd has failed to start, or it is doing its initial deploy that may
      echo take a long time. This should only happen once. If you are continuing to see
      echo this, please contact an administrator.
    )
    set VIP_HTTPD_TEMP_STARTED=
  )
)
goto done

:killall
for %%t in (%TASKS%) do (
  schtasks /end /TN %%t_%VIP_DAEMON_POSTFIX%
  if /i "%%t"=="rabbitmq" (
    for /F "" %%i in ('python -m voxel_globe.tools.find_process erl.exe rabbitmq') do (
      taskkill /fi "PID eq %%i" /f
    )
    taskkill /im %VIP_RABBITMQ_DAEMON% /f
  )
  if /i "%%t"=="postgresql" (
    taskkill /im postgres.exe /f
  )
  if /i "%%t"=="celeryd" (
    for /F "" %%i in ('python -m voxel_globe.tools.find_process python.exe celery') do (
      taskkill /fi "PID eq %%i" /f
    )
  )
  if /i "%%t"=="flower" (
    for /F "" %%i in ('python -m voxel_globe.tools.find_process python.exe flower') do (
      taskkill /fi "PID eq %%i" /f
    )
  )
  if /i "%%t"=="notebook" (
    for /F "" %%i in ('python -m voxel_globe.tools.find_process python.exe notebook') do (
      taskkill /fi "PID eq %%i" /f
    )
  )
)
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
      if errorlevel 1 taskkill /im postgres.exe /f
    )
  )
  if /i "%%t"=="httpd" (
    for /l %%q in (1, 1, 5) do (
      if !VIP_HTTPD_TEMP_STOPPED! NEQ 1 (
        python -c "import urllib2; exec('try:\n  urllib2.urlopen(\'http://localhost:%VIP_HTTPD_PORT%/\', timeout=10)\nexcept urllib2.HTTPError:\n  exit(0)')" > NUL 2>&1
        if "!errorlevel!" NEQ "0" set VIP_HTTPD_TEMP_STOPPED=1
        echo Waiting for httpd server to go down... %%q
        timeout /T 1 /NOBREAK > nul
      )
    )
    if !VIP_HTTPD_TEMP_STOPPED! NEQ 1 (
      echo I give up
    )
    set VIP_HTTPD_TEMP_STOPPED=
  )

  if /i "%%t"=="notebook" (
    for /l %%q in (1, 1, 5) do (
      if !VIP_NOTEBOOK_TEMP_STOPPED! NEQ 1 (
        python -c "import urllib2; exec('try:\n  urllib2.urlopen(\'http://localhost:%VIP_NOTEBOOK_PORT%/\', timeout=10)\nexcept urllib2.HTTPError:\n  exit(0)')" > NUL 2>&1
        if "!errorlevel!" NEQ "0" set VIP_NOTEBOOK_TEMP_STOPPED=1
        echo Waiting for notebook server to go down... %%q
        timeout /T 1 /NOBREAK > nul
      )
    )
    if !VIP_NOTEBOOK_TEMP_STOPPED! NEQ 1 (
      echo I give up
    )
    set VIP_NOTEBOOK_TEMP_STOPPED=
  )
)
if "%VIP_RESTART%" == "1" (
  set VIP_RESTART=
  daemon.bat %1 start
)
goto done

:restart
set VIP_RESTART=1
goto stop
REM for %%t in (%TASKS%) do schtasks /end /TN %%t_%VIP_DAEMON_POSTFIX%
REM for %%t in (%TASKS%) do schtasks /run /TN %%t_%VIP_DAEMON_POSTFIX%
REM call daemon.bat %1 stop
REM call daemon.bat %1 start
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
