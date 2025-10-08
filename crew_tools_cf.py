# crew_tools_cf.py — outils Companion Factory pour CrewAI
from pathlib import Path
import os, subprocess, textwrap
from dotenv import dotenv_values
from crewai.tools import tool

ROOT = Path(__file__).resolve().parent

def _load_env_into(env: dict, env_file: Path):
    if env_file.exists():
        for k, v in dotenv_values(str(env_file)).items():
            if v is not None:
                env[k] = str(v)

@tool("run_smoke")
def run_smoke(instance_label: str) -> str:
    """Exécute instances/<label>/smoke_test.bat et renvoie la sortie brute.
    Suppose que le serveur Flask de l'instance est déjà lancé (flask run)."""
    inst_dir = ROOT / "instances" / instance_label
    bat = inst_dir / "smoke_test.bat"
    if not bat.exists():
        return f"ERROR: {bat} not found"
    env = os.environ.copy()
    _load_env_into(env, inst_dir / ".env")
    try:
        cp = subprocess.run(
            ["cmd", "/c", str(bat)],
            cwd=str(inst_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = (cp.stdout or "") + ("\n" + (cp.stderr or "") if cp.stderr else "")
        # On renvoie un extrait raisonnable pour éviter d'inonder le LLM
        return textwrap.shorten(out.replace("\r",""), width=1800, placeholder=" ...")
    except Exception as e:
        return f"ERROR: run_smoke failed: {e!r}"
