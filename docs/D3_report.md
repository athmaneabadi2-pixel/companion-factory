# Day 3 — Report (récap)

## Fait ✅
- Cursor — best practices : OK (`docs/cursor_best_practices.md`)
- CrewAI — best practices + snippets : OK (`docs/crewai_best_practices.md`)
- Intégration locale : OK (tools + runner + smoke)
  - Tools : `tool_generate_instance.py`, `tool_run_smoke.py`
  - Runner : `d3c_demo.py` → status "OK"
  - Smoke : `instances/demo11/smoke_test.bat` (HC=200 / IC=200)
  - Stub : `server.py` (local)

## Décisions 🧭
- IDE : Cursor adopté (prompts courts, itérations, refactor guidé)
- CrewAI : agents étroits, tasks avec DoD, process séquentiel, verbose=True
- Validation : smoke 200/200 + rapport JSON

## À faire (D3 → D4) 📌
- Compléter `docs/D3_links.md` (6–10 liens qualifiés)
- D4 : mini-crew Dev/Test qui génère une instance et lance le smoke
- Critères D4 : instance créée, smoke OK, rapport crew archivé

## Risques & garde-fous 🛡
- Batch Windows (quoting) → scripts simples, labels GOTO, capture HTTP via fichier tmp
- Hallucinations LLM → DoD explicite + tests minimaux
