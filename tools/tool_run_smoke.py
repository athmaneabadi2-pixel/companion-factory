import subprocess, os, json, sys

def run(label: str) -> dict:
    bat = os.path.join("instances", label, "smoke_test.bat")
    if not os.path.exists(bat):
        return {"ok": False, "code": 2, "out": f"not found: {bat}"}
    res = subprocess.run(["cmd", "/c", bat], capture_output=True, text=True)
    out = (res.stdout or res.stderr or "").strip()
    return {"ok": res.returncode == 0, "code": res.returncode, "out": out[-2000:]}

if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "demo10"
    print(json.dumps(run(label), ensure_ascii=False))
