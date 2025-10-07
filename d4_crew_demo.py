from dotenv import load_dotenv; load_dotenv()
import os, sys, time, subprocess, json, urllib.request, urllib.error

# --- Helpers ---
def healthy(host: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(host.rstrip("/") + "/health", timeout=timeout) as r:
            return r.getcode() == 200
    except Exception:
        return False

def autostart_server(host: str):
    if healthy(host):
        return None
    try:
        proc = subprocess.Popen(
            ["python", "server.py"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        for _ in range(20):  # ~10s max
            if healthy(host):
                break
            time.sleep(0.5)
        return proc
    except Exception:
        return None

# --- Params ---
label = sys.argv[1] if len(sys.argv) > 1 else "demo12"
tz = sys.argv[2] if len(sys.argv) > 2 else "Europe/Paris"
host = os.environ.get("HOST", "http://127.0.0.1:5000")

# --- Auto-start serveur local si /health KO ---
server_proc = autostart_server(host)

# --- CrewAI (optionnel) : ne pas planter si clé absente/invalide ---
run_crew = bool(os.getenv("OPENAI_API_KEY"))
plan_done = False
if run_crew:
    try:
        from crewai import Agent, Task, Crew, Process
        dev = Agent(
            role="Dev Python",
            goal="Préparer une instance minimale depuis le template (nom + timezone) sans fuite de secrets.",
            backstory="Dév pragmatique : petits pas, PEP8, explique ses choix.",
            verbose=True
        )
        tester = Agent(
            role="Test/QA",
            goal="Valider que /health et /internal/send répondent 200 via le script de smoke.",
            backstory="Testeur strict : DoD clair, résultat binaire OK/KO.",
            verbose=True
        )
        t_plan_dev = Task(
            description=f"Écris un plan concis (5 points) pour créer l’instance '{label}' en local, "
                        f"puis indique les fichiers attendus et les risques.",
            agent=dev, expected_output="Markdown en 5 points + liste de fichiers + 3 risques."
        )
        t_plan_test = Task(
            description=f"Écris les critères de test pour l’instance '{label}' : endpoints, codes HTTP, et condition de succès.",
            agent=tester, expected_output="Checklist de critères (codes attendus) + condition de succès."
        )
        crew = Crew(agents=[dev, tester], tasks=[t_plan_dev, t_plan_test], process=Process.sequential)
        _ = crew.kickoff()
        plan_done = True
    except Exception as e:
        print(f"[WARN] CrewAI plan ignoré ({e.__class__.__name__}: {e})", file=sys.stderr)
else:
    print("[INFO] OPENAI_API_KEY manquant : CrewAI plan désactivé.", file=sys.stderr)

# --- Actions concrètes (toujours) ---
from tools.tool_generate_instance import generate
from tools.tool_run_smoke import run

gen = generate(label, tz)
smk = run(label)

report = {
    "label": label,
    "timezone": tz,
    "generated": gen,
    "smoke": smk,
    "crew_plan": "done" if plan_done else "skipped",
    "status": "OK" if smk.get("ok") else "KO"
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if smk.get("ok") else 1)
