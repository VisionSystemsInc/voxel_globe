@echo off

%~dp0start_manage.bat collectstatic

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause
