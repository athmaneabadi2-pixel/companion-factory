@echo off
setlocal enabledelayedexpansion

:: Args
set "LABEL=%~1"
set "NAME=%~2"
if "%LABEL%"=="" (
  echo Usage: factory_new_and_push.bat demo06 "Nom Affiche"
  exit /b 1
)
if "%NAME%"=="" set "NAME=%LABEL%"

:: Dossier factory
cd "%HOMEPATH%\Downloads\companion-factory" || (
  echo [ERR] Dossier factory introuvable: %HOMEPATH%\Downloads\companion-factory
  exit /b 1
)

:: Garde-fou: ne pas écraser une instance existante
if exist "instances\%LABEL%\" (
  echo [ERR] L'instance instances\%LABEL% existe déjà. Choisis un autre label.
  exit /b 1
)

:: Génération depuis le template
python cli\companion_new.py --label "%LABEL%" --display-name "%NAME%" --timezone "Europe/Paris" --features weather,sports,checkin || (
  echo [ERR] companion_new.py a échoué.
  exit /b 1
)

:: Git init dans l'instance
cd "instances\%LABEL%" || (
  echo [ERR] Dossier instances\%LABEL% introuvable.
  exit /b 1
)

(
  echo .venv
  echo .env
  echo __pycache__
) > .gitignore

git init
git branch -M main
git add .
git commit -m "chore: init %LABEL%"

:: Création du repo GitHub (nécessite gh auth login)
gh repo create "%LABEL%" --public --source=. --remote=origin --push --confirm || (
  echo [WARN] Echec gh repo create. Crée le repo manuellement puis:
  echo   git remote add origin https://github.com/<ton-user>/%LABEL%.git
  echo   git push -u origin main
)

echo.
echo ==== Prochaines etapes ====
echo 1) Render: Build "pip install -r requirements.txt"
echo    Start "gunicorn app:app --bind 0.0.0.0:^$PORT --workers 2"
echo    ENV: OPENAI_API_KEY, PYTHON_VERSION=3.11.9, INTERNAL_TOKEN=%LABEL%-check-123
echo    + TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SANDBOX_FROM=whatsapp:+14155238886, USER_WHATSAPP_TO=whatsapp:+33XXXXXXXXX
echo 2) Twilio Sandbox: webhook https://^<service^>.onrender.com/whatsapp/webhook
echo 3) Tests rapides:
echo    set HOST=https://^<service^>.onrender.com
echo    curl.exe -s -o NUL -w "HEALTH %%%%{http_code}\n" %%%%HOST%%%%/health
echo    curl.exe -s -o NUL -w "SEND %%%%{http_code}\n" -X POST %%%%HOST%%%%/internal/send?format=text -H "X-Token: %LABEL%-check-123" -H "Content-Type: application/json" -d "{\"text\":\"ping\"}"
echo    curl.exe -s -o NUL -w "CHECKIN %%%%{http_code}\n" -X POST %%%%HOST%%%%/internal/checkin -H "X-Token: %LABEL%-check-123"
endlocal
