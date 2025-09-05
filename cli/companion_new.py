#!/usr/bin/env python3
import argparse, os, json, shutil
from pathlib import Path

RUN_DEV_BAT = r"""@echo off
cd /d %~dp0
if not exist .venv\Scripts\activate.bat (
  py -m venv .venv
  call .venv\Scripts\activate
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate
)
set FLASK_ENV=development
python app.py
"""

SMOKE_TEST_BAT = r"""@echo off
setlocal
echo [Smoke] Test /health...
curl.exe -s http://127.0.0.1:5000/health | find "\"status\":\"ok\"" >nul || (echo [X] /health KO & exit /b 1)
echo [Smoke] Test /internal/send...
curl.exe -s -X POST http://127.0.0.1:5000/internal/send -H "Content-Type: application/json" -d "{\"text\":\"Salut\"}" | find "\"ok\": true" >nul || (echo [X] /internal/send KO & exit /b 1)
echo [OK] Smoke test passe.
exit /b 0
"""

def drop_helper_scripts(dest_dir: Path):
    (dest_dir / "run-dev.bat").write_text(RUN_DEV_BAT, encoding="utf-8")
    (dest_dir / "smoke_test.bat").write_text(SMOKE_TEST_BAT, encoding="utf-8")

PLACEHOLDERS = {
    "__DISPLAY_NAME__": "display_name",
    "__LABEL__": "label",
    "__TIMEZONE__": "timezone"
}

def replace_placeholders_in_file(file_path: Path, mapping: dict):
    text = file_path.read_text(encoding="utf-8")
    for placeholder, key in PLACEHOLDERS.items():
        text = text.replace(placeholder, mapping[key])
    if "__FEATURES_LIST__" in text:
        features = mapping.get("features", [])
        serialized = ",".join([f'"{f}"' for f in features]) if features else ""
        text = text.replace("__FEATURES_LIST__", serialized)
    file_path.write_text(text, encoding="utf-8")

def copy_and_fill_template(template_dir: Path, dest_dir: Path, mapping: dict):
    if dest_dir.exists():
        raise SystemExit(f"Destination already exists: {dest_dir}")
    shutil.copytree(template_dir, dest_dir)
    for p in dest_dir.rglob("*"):
        if p.is_file():
            if p.suffix.lower() in {".py",".md",".txt",".yaml",".yml",".sample",".sql",".json"} or p.name in {"render.yaml","Procfile"}:
                replace_placeholders_in_file(p, mapping)

def main():
    parser = argparse.ArgumentParser(description="Generate a new Companion bot project from template.")
    parser.add_argument("--label", required=True, help="Instance label, e.g., demo01")
    parser.add_argument("--display-name", required=True, help="Displayed bot name, e.g., 'Noura'")
    parser.add_argument("--timezone", default="Europe/Paris", help="Timezone string")
    parser.add_argument("--features", default="", help="Comma-separated features, e.g. weather,sports,checkin")
    parser.add_argument("--profile", help="Path to a profile JSON to include as profile.json")
    parser.add_argument("--out-dir", default="instances", help="Parent directory where the instance will be created")
    parser.add_argument("--template", default="templates/companion_project", help="Template directory path")
    args = parser.parse_args()

    features = [f.strip() for f in args.features.split(",") if f.strip()]
    mapping = {
        "label": args.label,
        "display_name": args.display_name,
        "timezone": args.timezone,
        "features": features
    }

    template_dir = Path(args.template).resolve()
    out_parent = Path(args.out_dir).resolve()
    out_parent.mkdir(parents=True, exist_ok=True)
    dest_dir = out_parent / args.label

    copy_and_fill_template(template_dir, dest_dir, mapping)
    drop_helper_scripts(dest_dir)  # 👉 ajoute les helpers

    # profile
    if args.profile:
        src = Path(args.profile).resolve()
        if not src.exists():
            raise SystemExit(f"Profile not found: {src}")
        shutil.copy(src, dest_dir / "profile.json")
    else:
        example = dest_dir / "profile.example.json"
        if example.exists():
            (dest_dir / "profile.json").write_text(example.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"\n✅ Created new companion instance at: {dest_dir}\n")
    if os.name == "nt":
        print("Next steps (Windows CMD):")
        print(f"  1) cd {dest_dir}")
        print(r"  2) .\.venv\Scripts\activate  (ou double-clique run-dev.bat)")
        print(r"     - si la venv n'existe pas : py -m venv .venv & .\.venv\Scripts\activate & pip install -r requirements.txt")
        print(r"  3) copy .env.sample .env  (puis remplir)")
        print(r"  4) python app.py  (ou double-clique run-dev.bat)")
        print(r"  5) smoke_test.bat")
    else:
        print("Next steps (Unix):")
        print(f"  1) cd {dest_dir}")
        print("  2) python -m venv .venv && source .venv/bin/activate")
        print("  3) pip install -r requirements.txt")
        print("  4) cp .env.sample .env  &&  python app.py")

if __name__ == "__main__":
    main()
