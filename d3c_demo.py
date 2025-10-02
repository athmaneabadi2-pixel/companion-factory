import json, sys
from tools.tool_generate_instance import generate
from tools.tool_run_smoke import run

label = sys.argv[1] if len(sys.argv) > 1 else "demo11"
tz = sys.argv[2] if len(sys.argv) > 2 else "Europe/Paris"

gen = generate(label, tz)
smk = run(label)

report = {
    "label": label,
    "timezone": tz,
    "generated": gen,
    "smoke": smk,
    "status": "OK" if smk.get("ok") else "KO"
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if smk.get("ok") else 1)
