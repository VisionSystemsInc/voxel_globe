@echo off

call %~dp0/daemon.bat all status

net session >nul 2>&1
if %errorLevel% == 0 (
  echo %cmdcmdline% | find /i "%~0" >nul
  if not errorlevel 1 pause
)