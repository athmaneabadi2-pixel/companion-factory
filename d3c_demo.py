import json, sys, os, time, subprocess, urllib.request, urllib.error
from tools.tool_generate_instance import generate
from tools.tool_run_smoke import run

def healthy(host: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(host.rstrip("/") + "/health", timeout=timeout) as r:
            return r.getcode() == 200
    except Exception:
        return False

label = sys.argv[1] if len(sys.argv) > 1 else "demo11"
tz = sys.argv[2] if len(sys.argv) > 2 else "Europe/Paris"

host = os.environ.get("HOST", "http://127.0.0.1:5000")

# 0) Auto-start serveur si /health KO
server_proc = None
if not healthy(host):
    try:
        server_proc = subprocess.Popen(
            ["python", "server.py"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        for _ in range(20):  # ~10s max
            if healthy(host):
                break
            time.sleep(0.5)
    except Exception:
        pass  # on laissera le smoke remonter l’erreur le cas échéant

# 1) Générer/assurer l'instance
gen = generate(label, tz)

# 2) Lancer le smoke
smk = run(label)

report = {
    "label": label,
    "timezone": tz,
    "generated": gen,
    "smoke": smk,
    "status": "OK" if smk.get("ok") else "KO"
}
print(json.dumps(report, ensure_ascii=False, indent=2))

# NB: on ne tue pas server_proc (usage dev local)
raise SystemExit(0 if smk.get("ok") else 1)
