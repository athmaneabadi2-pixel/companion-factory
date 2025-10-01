# crew_cf.py — QA local pour Companion Factory (demo09)
# 1) Fait les checks HTTP en Python (health + internal/send)
# 2) Demande à CrewAI de résumer clairement l'état et les prochains pas.

from dotenv import load_dotenv
import os, requests, json
from crewai import Agent, Task, Crew, Process

# -- Charger la config de l'instance
load_dotenv("instances/demo09/.env")
BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
TOKEN = os.getenv("INTERNAL_TOKEN", "dev-123")

def check_health():
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        return {"ok": r.status_code == 200, "code": r.status_code, "body": r.text}
    except Exception as e:
        return {"ok": False, "code": "ERR", "error": str(e)}

def check_internal(text="ping"):
    try:
        r = requests.post(
            f"{BASE}/internal/send",
            headers={"X-Token": TOKEN, "Content-Type": "application/json"},
            json={"text": text},
            timeout=8,
        )
        # on renvoie un extrait pour éviter d'imprimer tout
        body = r.text
        if len(body) > 200:
            body = body[:200] + "..."
        return {"ok": r.status_code == 200, "code": r.status_code, "body": body}
    except Exception as e:
        return {"ok": False, "code": "ERR", "error": str(e)}

# -- Checks concrets
health = check_health()
internal = check_internal("Bonjour !")

# -- Agents qui rédigent un court rapport à partir des résultats
qa = Agent(
    role="QA Tester",
    goal="Analyser des résultats de tests HTTP et décider OK/KO.",
    backstory="Ingénieur QA qui va droit au but et propose 1-2 actions concrètes.",
    llm="gpt-4o-mini",
)
reporter = Agent(
    role="Reporter",
    goal="Produire un résumé simple pour l'équipe Companion Factory.",
    backstory="Sait expliquer le statut en 3 lignes max.",
    llm="gpt-4o-mini",
)

context = {
    "base": BASE,
    "health": health,
    "internal": internal,
}

t1 = Task(
    description=(
        "Voici des résultats JSON de tests HTTP pour une app Flask.\n"
        f"Context JSON:\n{json.dumps(context, ensure_ascii=False)}\n\n"
        "Travail: Dis en bullet points si /health et /internal/send sont OK ou KO "
        "avec les codes, puis propose 1–2 actions si KO."
    ),
    expected_output="Une liste succinte de bullet points statut + actions.",
    agent=qa,
)

t2 = Task(
    description=(
        "Prends la sortie du QA et écris un résumé final en 2-3 lignes max, clair, pour le tech lead."
    ),
    expected_output="Un court paragraphe clair.",
    agent=reporter,
)

crew = Crew(agents=[qa, reporter], tasks=[t1, t2], process=Process.sequential, verbose=True)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\nDONE:", f"health={health.get('code')}, internal={internal.get('code')} — {str(result)[:300]}")
