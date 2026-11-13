@echo off
setlocal
if defined PYTHON goto custom
python -X utf8 "%~dp0src\main.py" %*
exit /b %errorlevel%
:custom
"%PYTHON%" -X utf8 "%~dp0src\main.py" %*
exit /b %errorlevel%
