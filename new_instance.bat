@echo off
setlocal EnableExtensions

REM new_instance.bat — crée une instance + copie le template smoke_test.bat
REM Usage: new_instance.bat <label> [DisplayName] [Timezone] [Features]

if "%~1"=="" (
  echo Usage: new_instance.bat ^<label^> [DisplayName] [Timezone] [Features]
  exit /b 1
)

set "LABEL=%~1"
set "DISPLAY=%~2"
set "TZ=%~3"
set "FEAT=%~4"

if "%DISPLAY%"=="" set "DISPLAY=%LABEL%"
if "%TZ%"=="" set "TZ=Europe/Paris"
if "%FEAT%"=="" set "FEAT=weather,sports,checkin"

if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

python cli\companion_new.py --label "%LABEL%" --display-name "%DISPLAY%" --timezone "%TZ%" --features "%FEAT%"
if errorlevel 1 (
  echo [X] Generation KO
  exit /b 1
)

if exist "templates\instance\smoke_test.bat" (
  copy /y "templates\instance\smoke_test.bat" "instances\%LABEL%\smoke_test.bat" >nul
  echo [OK] smoke_test.bat copie dans instances\%LABEL%
) else (
  echo [!] Template templates\instance\smoke_test.bat introuvable
)

echo [DONE] Instance cree: instances\%LABEL%
exit /b 0
