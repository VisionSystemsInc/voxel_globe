@echo off
call %~dp0\..\wrap.bat python %~dp0\initialize_database.py

echo %cmdcmdline% | find /i "%~0" >nul
if not errorlevel 1 pause

