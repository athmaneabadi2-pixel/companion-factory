import json,io,sys
s=io.open(r"instances\demo06\profile.json","r",encoding="utf-8").read()
try:
    json.loads(s)
    print("OK: profile.json valide")
except Exception as e:
    print("JSON ERROR:", type(e).__name__, str(e)); sys.exit(1)
