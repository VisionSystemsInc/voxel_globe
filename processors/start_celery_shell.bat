1>2# : ^
'''
@echo off
setlocal
call %~dp0/../np2r.bat

%NPR_PYTHON_DIR%/python %*

exit /b
endlocal
'''