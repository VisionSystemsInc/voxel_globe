@echo off
setlocal
call %~dp0/np2r.bat

chcp 1252 > NUL
psql.exe %NPR_POSTGRESQL_CREDENTIALS% %NPR_POSTGRESQL_DATABASE_NAME% %*

endlocal