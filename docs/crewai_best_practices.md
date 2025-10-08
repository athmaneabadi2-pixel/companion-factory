# CrewAI — Bonnes pratiques (D3-B)

## Règles (8)
1. Un agent = un rôle (périmètre étroit).
2. Backstory courte + goal mesurable (1–2 phrases).
3. Tasks avec DoD clair (format attendu).
4. Process : commencer séquentiel, paralléliser plus tard.
5. Logs : `verbose=True` pour déboguer.
6. Outils : fonctions simples, I/O typées, effets de bord minimisés.
7. Robustesse : timeouts, retries, idempotence.
8. Tests : dry-run (mocks) + smoke sur instance générée.

## Snippet : Agent
```python
from crewai import Agent
dev_agent = Agent(
    role="Dev Python",
    goal="Créer une instance depuis le template (nom, timezone)",
    backstory="Pragmatique, PEP8, petit pas + tests.",
    verbose=True,
)
```

## Snippet : Task avec DoD
```python
from crewai import Task
task_make_instance = Task(
    description="Créer l'instance {label} et résumer les fichiers générés.",
    agent=dev_agent,
    expected_output={"format": "markdown", "contains": ["chemin", "fichiers", "étapes"]}
)
```

## Snippet : Crew + kickoff
```python
from crewai import Crew, Process
crew = Crew(agents=[dev_agent], tasks=[task_make_instance], process=Process.sequential)
print(crew.kickoff())
```

## Snippet : Outil tool_run_smoke
```python
import subprocess, os
def tool_run_smoke(label: str) -> dict:
    bat = os.path.join("instances", label, "smoke_test.bat")
    if not os.path.exists(bat):
        return {"ok": False, "code": 2, "out": f"missing {bat}"}
    res = subprocess.run(["cmd","/c", bat], capture_output=True, text=True)
    return {"ok": res.returncode == 0, "code": res.returncode, "out": (res.stdout or res.stderr or "")[:2000]}
```

## Snippet : Check version
```bash
python -c "import crewai; print('CrewAI', crewai.__version__)"



```
