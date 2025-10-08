# tests/test_smoke.py
import os, time, json, subprocess, sys, signal, shlex
from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")
START_LOCAL = os.getenv("START_LOCAL", "")
START_CMD = os.getenv("START_CMD", "")  # e.g. .\scripts\run_server.bat  OR  python app.py
LOG_PATH = REPO_ROOT / "tests" / ".server.log"

def _is_up():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def _guess_start_cmd():
    if START_CMD:
        return START_CMD
    # Heuristiques
    candidates = [
        "app.py",
        "server.py",
        "main.py",
        str(Path("scripts") / "run_server.bat"),
    ]
    for c in candidates:
        p = REPO_ROOT / c
        if p.exists():
            if p.suffix.lower() == ".bat":
                return str(p)  # batch
            return f"{shlex.quote(sys.executable)} {shlex.quote(str(p))}"
    # Dernier recours: flask run si FLASK_APP défini
    if os.getenv("FLASK_APP"):
        # On force le port cohérent avec BASE_URL
        return f"{shlex.quote(sys.executable)} -m flask run --port {_port_from_baseurl()}"
    # Rien trouvé
    return ""

def _port_from_baseurl():
    u = urlparse(BASE_URL)
    if u.port:
        return u.port
    return 443 if u.scheme == "https" else 80

def _start_server():
    cmd = _guess_start_cmd()
    if not cmd:
        raise RuntimeError(
            "Aucun START_CMD valide. Définis START_CMD (ex: .\\scripts\\run_server.bat ou 'python app.py')."
        )

    env = os.environ.copy()
    # Aligne les variables de port usuelles
    env.setdefault("PORT", str(_port_from_baseurl()))
    env.setdefault("FLASK_RUN_PORT", str(_port_from_baseurl()))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(LOG_PATH, "wb")

    # Windows: .bat => shell=True ; sinon liste
    creationflags = 0
    if sys.platform.startswith("win"):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    if cmd.lower().endswith(".bat"):
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=log_f,
            stderr=subprocess.STDOUT,
            shell=True,
            creationflags=creationflags,
            env=env,
        )
    else:
        proc = subprocess.Popen(
            shlex.split(cmd),
            cwd=str(REPO_ROOT),
            stdout=log_f,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
            env=env,
        )
    return proc, log_f

@pytest.fixture(scope="session", autouse=True)
def ensure_server():
    need_start = START_LOCAL == "1" or not _is_up()
    proc = None
    log_f = None

    if need_start:
        proc, log_f = _start_server()

        # Attente /health (60s max)
        deadline = time.time() + 60
        while time.time() < deadline:
            if _is_up():
                break
            time.sleep(0.5)
        else:
            # Dump de fin de log pour debug
            try:
                if log_f:
                    log_f.flush()
                with open(LOG_PATH, "rb") as f:
                    tail = f.read()[-4000:]
            except Exception:
                tail = b""
            # Stoppe le process
            if proc and proc.poll() is None:
                if sys.platform.startswith("win"):
                    try:
                        proc.send_signal(signal.CTRL_BREAK_EVENT)
                    except Exception:
                        pass
                proc.terminate()
            raise RuntimeError(
                f"Serveur introuvable sur {BASE_URL} après 60s.\n"
                f"Commande: {START_CMD or _guess_start_cmd()}\n"
                f"Dernières lignes du log ({LOG_PATH}):\n{tail.decode(errors='ignore')}"
            )

    yield

    if need_start and proc and proc.poll() is None:
        if sys.platform.startswith("win"):
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                pass
        proc.terminate()
    if log_f:
        try:
            log_f.close()
        except Exception:
            pass

def test_health_200():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert str(data.get("status", "")).lower() == "ok"

def test_internal_send_200():
    headers = {"Content-Type": "application/json"}
    if INTERNAL_TOKEN:
        headers["X-Token"] = INTERNAL_TOKEN
    payload = {"text": "ping"}

    r = requests.post(f"{BASE_URL}/internal/send", headers=headers, data=json.dumps(payload), timeout=10)
    assert r.status_code == 200

    content_type = r.headers.get("Content-Type", "")
    if "application/json" in content_type:
        # DoD minimal: JSON décodable (peu importe les clés)
        _ = r.json()
    else:
        # Sinon: juste un body non vide
        assert len(r.text.strip()) > 0
