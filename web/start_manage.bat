@echo off

call %~dp0..\np2r.bat %*

set PYTHONPATH=%NPR_CELERY_PROCESSORS%

%~dp0..\wrap.bat python %~dp0manage.py %*