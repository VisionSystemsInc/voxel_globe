@echo off

setlocal

call %~dp0..\vip.bsh

pg_restore %VIP_POSTGRESQL_CREDENTIALS% -d %VIP_POSTGRESQL_DATABASE_NAME% %*

endlocal