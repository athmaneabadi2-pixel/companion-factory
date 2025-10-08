@echo off
setlocal EnableExtensions
if "%~1"=="" (
  echo Usage: %~nx0 ^<label^>
  exit /b 1
)
cd /d %~dp0\..\instances\%1
call smoke_test.bat
exit /b %errorlevel%
