@echo off
SET mypath=%~dp0%
%mypath%fleta_daemon.exe stop all
%mypath%fleta_daemon.exe start all

echo Pressed Enter key........
set /p input=