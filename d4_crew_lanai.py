from dotenv import load_dotenv; load_dotenv()
import os, sys, time, subprocess, json, urllib.request, urllib.error
from datetime import datetime

# --- Helpers (auto-start serveur / health) ---
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
        proc = subprocess.Popen(["python", "server.py"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(20):  # ~10s
            if healthy(host): break
            time.sleep(0.5)
        return proc
    except Exception:
        return None

# --- Params ---
label = sys.argv[1] if len(sys.argv) > 1 else "demo13"
tz = os.getenv("TIMEZONE", "Europe/Paris")
host = os.getenv("HOST", "http://127.0.0.1:5000")

# --- Start server if needed ---
server_proc = autostart_server(host)

# --- CrewAI (optionnel) : PM/Dev/Test pour trace écrite ---
crew_plan = "skipped"
if os.getenv("OPENAI_API_KEY"):
    try:
        from crewai import Agent, Task, Crew, Process
        pm = Agent(
            role="PM",
            goal="Rédiger une spec minimale pour une instance locale basée sur le template minimal.",
            backstory="PM concis : objectifs, périmètre, risques.",
            verbose=True
        )
        dev = Agent(
            role="Dev Python",
            goal="Créer une instance minimale (.env + smoke_test.bat) sans fuite de secrets.",
            backstory="Dév pragmatique : petits pas, PEP8.",
            verbose=True
        )
        tester = Agent(
            role="Test/QA",
            goal="Valider /health et /internal/send (codes 200) via le smoke.",
            backstory="Testeur strict, DoD binaire.",
            verbose=True
        )

        t_spec = Task(
            description=(f"Écris une spec ultra-courte pour l’instance '{label}' "
                         f"(objectif, fichiers attendus: `.env`, `smoke_test.bat`, risques clés)."),
            agent=pm, expected_output="Spec Markdown en ≤10 lignes."
        )
        t_plan_dev = Task(
            description=(f"Plan (5 points) pour générer '{label}' depuis le template MINIMAL. "
                         f"N'utiliser que `.env` et `smoke_test.bat`. Liste 3 risques."),
            agent=dev, expected_output="Plan 5 points + ['.env','smoke_test.bat'] + 3 risques."
        )
        t_checklist = Task(
            description=(f"Checklist de test pour '{label}': /health=200 et /internal/send=200. "
                         f"Condition de succès unique."),
            agent=tester, expected_output="Checklist endpoints + codes + condition de succès."
        )

        Crew(agents=[pm, dev, tester],
             tasks=[t_spec, t_plan_dev, t_checklist],
             process=Process.sequential).kickoff()
        crew_plan = "done"
    except Exception as e:
        print(f"[WARN] CrewAI plan ignoré ({e.__class__.__name__}: {e})", file=sys.stderr)

# --- Actions concrètes : générer + smoke ---
from tools.tool_generate_instance import generate
from tools.tool_run_smoke import run
gen = generate(label, tz)
smk = run(label)

# --- Rapport fichiers ---
os.makedirs("docs", exist_ok=True)
report = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "label": label,
    "timezone": tz,
    "host": host,
    "generated": gen,
    "smoke": smk,
    "crew_plan": crew_plan,
    "status": "OK" if smk.get("ok") else "KO"
}
with open("docs/last_run.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

md = [
    f"# Run report — {report['timestamp']}",
    f"- **Label** : {label}",
    f"- **Timezone** : {tz}",
    f"- **Host** : {host}",
    f"- **Instance path** : {gen.get('instance_path')}",
    f"- **Files** : {', '.join(gen.get('files', []))}",
    f"- **Smoke** : {'OK' if smk.get('ok') else 'KO'} (code={smk.get('code')})",
    "```",
    (smk.get("out") or "")[:2000],
    "```",
    f"- **Crew plan** : {crew_plan}",
    f"- **Status** : {report['status']}",
]
with open("docs/last_run.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["status"] == "OK" else 1)
