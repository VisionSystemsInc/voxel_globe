@echo off
setlocal
call %~dp0/np2r.bat

chcp 1252 > NUL
psql.exe %VIP_POSTGRESQL_CREDENTIALS% %VIP_POSTGRESQL_DATABASE_NAME% %*

endlocal