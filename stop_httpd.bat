@echo off

echo Administrative permissions required. Detecting permissions...
net session >nul 2>&1
if not %errorLevel% == 0 (
  echo Failure: Current permissions inadequate. Aquiring elevated permissions!
  setlocal DisableDelayedExpansion
  set "batchPath=%~0"
  setlocal EnableDelayedExpansion
  %DRYRUN%ECHO Set UAC = CreateObject^("Shell.Application"^) > "%~dp0\OEgetPrivileges.vbs" 
  %DRYRUN%ECHO UAC.ShellExecute "!batchPath!", "ELEV", "", "runas", 1 >> "%~dp0\OEgetPrivileges.vbs" 
  %DRYRUN%"%~dp0\OEgetPrivileges.vbs" 
  %DRYRUN%exit /B 1
)
echo Elevated permissions detected

del %~dp0\OEgetPrivileges.vbs > NUL 2>&1

schtasks /end /TN Httpd_daemon