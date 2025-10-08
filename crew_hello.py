# crew_hello.py — Dev -> Reviewer, sauvegarde du code généré
from pathlib import Path
import re
from dotenv import load_dotenv
load_dotenv("instances/demo09/.env")

from crewai import Agent, Task, Crew, Process

dev = Agent(
    role="DevJunior",
    goal="Écrire une fonction Python hello(name) qui renvoie 'Hello {name}!'",
    backstory="Développeur Python qui suit PEP8.",
    llm="gpt-4o-mini",
)
review = Agent(
    role="CodeReviewer",
    goal="Relire et renvoyer une version finale propre de la fonction hello(name).",
    backstory="Relecteur attentif qui vérifie simplicité et clarté.",
    llm="gpt-4o-mini",
)

t1 = Task(
    description="Écris la fonction hello(name) conforme PEP8, avec docstring courte.",
    expected_output="Un bloc de code Python complet et exécutable définissant hello(name).",
    agent=dev,
)
t2 = Task(
    description="Relis la fonction produite et renvoie la version finale (un seul bloc de code).",
    expected_output="Un unique bloc de code Python avec la fonction hello(name).",
    agent=review,
)

crew = Crew(agents=[dev, review], tasks=[t1, t2], process=Process.sequential, verbose=True)

def extract_code(text: str) -> str:
    # récupère le 1er bloc ```python ... ``` ou ``` ... ```
    m = re.search(r"```(?:python)?\s*(.+?)```", text, flags=re.S)
    return m.group(1).strip() if m else text.strip()

if __name__ == "__main__":
    result = crew.kickoff(inputs={"name": "Noura"})
    final_text = str(result)
    code = extract_code(final_text)

    out_dir = Path("crew_outputs"); out_dir.mkdir(exist_ok=True)
    (out_dir / "__init__.py").write_text("")  # pour import
    (out_dir / "hello.py").write_text(code, encoding="utf-8")

    print("\nDONE: saved ->", out_dir / "hello.py")
