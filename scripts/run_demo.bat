@echo off
setlocal EnableExtensions
if "%~1"=="" (
  echo Usage: %~nx0 ^<label^>
  exit /b 1
)
cd /d %~dp0\..
call .venv\Scripts\activate
python d4_crew_lanai.py %1
exit /b %errorlevel%