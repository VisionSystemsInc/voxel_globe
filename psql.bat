@echo off
setlocal
call %~dp0vip.bat

chcp 1252 > NUL
psql.exe %VIP_POSTGRESQL_CREDENTIALS% %VIP_POSTGRESQL_DATABASE_NAME% %*

endlocal