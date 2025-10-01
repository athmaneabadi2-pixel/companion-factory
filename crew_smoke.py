# crew_smoke.py — Lance smoke_test.bat (demo09) puis fait résumer par CrewAI
from pathlib import Path
import subprocess, json, os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# --- Contexte / chemins
INSTANCE = os.getenv("INSTANCE_LABEL", "demo09")
ROOT = Path(__file__).parent
INST_DIR = ROOT / "instances" / INSTANCE
BAT = INST_DIR / "smoke_test.bat"

# --- Charger les .env
# (1) racine si présent (facultatif)
load_dotenv(ROOT / ".env", override=False)
# (2) .env de l'instance (prioritaire : contient INTERNAL_TOKEN, OPENAI_API_KEY, etc.)
load_dotenv(INST_DIR / ".env", override=True)

def run_smoke() -> dict:
    if not BAT.exists():
        return {"ok": False, "error": f"Fichier introuvable: {BAT}"}
    try:
        r = subprocess.run(
            ["cmd", "/c", str(BAT)],
            cwd=str(INST_DIR),            # <-- exécuter DANS l'instance
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")
        # OK si pas de "[X]" et retour == 0
        ok = ("[X]" not in out) and (r.returncode == 0)
        return {"ok": ok, "returncode": r.returncode, "output_tail": out[-1200:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# 1) Exécuter le smoke
result = run_smoke()

# 2) Agents CrewAI pour analyser & résumer
qa = Agent(
    role="QA Runner",
    goal="Interpréter un log de smoke test et dire OK/KO + prochaines actions.",
    backstory="Ingénieur QA pragmatique qui parle en puces.",
    llm="gpt-4o-mini",
)
reporter = Agent(
    role="Reporter",
    goal="Rédiger une conclusion en 2 lignes max pour le tech lead.",
    backstory="Synthèse claire et courte.",
    llm="gpt-4o-mini",
)

context = {"instance": INSTANCE, "bat": str(BAT), "result": result}

t1 = Task(
    description=(
        "Voici le résultat JSON d'un smoke test Windows (.bat). "
        "Analyse-le et dis en bullet points si c'est OK ou KO, "
        "quels endpoints ont probablement échoué et donne 1–2 actions concrètes.\n\n"
        f"CONTEXTE JSON:\n{json.dumps(context, ensure_ascii=False)}"
    ),
    expected_output="Puces: statut + points clés + 1–2 actions.",
    agent=qa,
)
t2 = Task(
    description="Écris une conclusion en 2 lignes max pour le tech lead.",
    expected_output="Deux lignes max, claires.",
    agent=reporter,
)

crew = Crew(agents=[qa, reporter], tasks=[t1, t2], process=Process.sequential, verbose=True)

if __name__ == "__main__":
    summary = crew.kickoff()
    status = "SMOKE=OK" if result.get("ok") else "SMOKE=KO"
    print(f"\nDONE: {status} — {str(summary)[:300]}")
