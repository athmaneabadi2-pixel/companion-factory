import os, shutil, json, sys

TEMPLATE_SMOKE = os.path.join("templates", "instance", "smoke_test.bat")

FALLBACK_SMOKE = r"""@echo off
setlocal
if "%HOST%"=="" (
  echo HOST non defini. Definis HOST=http://127.0.0.1:5000
  exit /b 1
)
if "%INTERNAL_TOKEN%"=="" (
  echo INTERNAL_TOKEN non defini. Ajoute-le dans .env
  exit /b 1
)

echo === /health ===
curl.exe -s -o NUL -w "HEALTH %%{http_code}\n" "%HOST%/health" || exit /b 1

echo === /internal/send ===
curl.exe -s -o NUL -w "INTERNAL %%{http_code}\n" -X POST ^
  -H "X-Token: %INTERNAL_TOKEN%" -H "Content-Type: application/json" ^
  "%HOST%/internal/send?format=text" -d "{\"text\":\"ping\"}" || exit /b 1

exit /b 0
"""

def generate(label: str, timezone: str = "Europe/Paris") -> dict:
    dst = os.path.join("instances", label)
    os.makedirs(dst, exist_ok=True)

    # 1) smoke_test.bat
    smk = os.path.join(dst, "smoke_test.bat")
    if os.path.exists(TEMPLATE_SMOKE):
        shutil.copyfile(TEMPLATE_SMOKE, smk)
    else:
        with open(smk, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(FALLBACK_SMOKE)

    # 2) .env minimal (⚠️ ne mets jamais de secrets ici dans le chat)
    envp = os.path.join(dst, ".env")
    if not os.path.exists(envp):
        with open(envp, "w", encoding="utf-8", newline="\r\n") as f:
            f.write("OPENAI_API_KEY=\n")           # à remplir en local / ENV Render
            f.write("INTERNAL_TOKEN=dev-123\n")    # aligné avec ton backend local
            f.write(f"TIMEZONE={timezone}\n")
            f.write("HOST=http://127.0.0.1:5000\n")# pour les tests locaux

    return {"instance_path": dst, "files": sorted(os.listdir(dst))}

if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "demo11"
    tz = sys.argv[2] if len(sys.argv) > 2 else "Europe/Paris"
    print(json.dumps(generate(label, tz), ensure_ascii=False))
