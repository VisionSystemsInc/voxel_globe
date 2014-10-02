@echo off

setlocal

call %~dp0..\vip.bsh

pg_dump %VIP_POSTGRESQL_CREDENTIALS% %VIP_POSTGRESQL_DATABASE_NAME%

endlocal