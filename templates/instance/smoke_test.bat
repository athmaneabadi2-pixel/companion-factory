@echo off
setlocal EnableExtensions

REM === Charger BASE_URL et INTERNAL_TOKEN depuis .env si présents ===
set "BASE=http://127.0.0.1:5000"
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
  if /i "%%~a"=="BASE_URL" set "BASE=%%~b"
  if /i "%%~a"=="INTERNAL_TOKEN" set "INTERNAL_TOKEN=%%~b"
)
if not defined INTERNAL_TOKEN set "INTERNAL_TOKEN=dev-123"

echo [Smoke] Test /health...
REM -f = fail sur HTTP>=400 ; -s silencieux ; -S affiche les erreurs si échec
curl.exe -s -S -f "%BASE%/health" >NUL
if errorlevel 1 (
  echo [X] /health KO
  exit /b 1
) else (
  echo [OK] /health est ok.
)

echo [Smoke] Test /internal/send...
curl.exe -s -S -f -X POST "%BASE%/internal/send" ^
  -H "X-Token: %INTERNAL_TOKEN%" -H "Content-Type: application/json" ^
  -d "{\"text\":\"ping\"}" >NUL
if errorlevel 1 (
  echo [X] /internal/send KO
  exit /b 1
) else (
  echo [OK] /internal/send est ok.
)

exit /b 0
