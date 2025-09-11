\# Operations — Companion Factory



\## Pré-requis (local)



\# Operations — Companion Factory



\## Pré-requis (local)



C:\\Users\\me\\companion-factory\\.venv\\Scripts\\activate

cd /d C:\\Users\\me\\companion-factory\\instances\\demo06

set "TOKEN=dev-123"

flask --app app run -p 5000





\## Smoke (local)





\## Smoke (prod)



set "BASE=https://<service>.onrender.com"

instances\\demo06\\ops\\smoke\_prod.bat %BASE% %TOKEN%





\## Diag (prod)



instances\\demo06\\ops\\diag\_prod.bat %BASE% %TOKEN%





\## Interpréter vite

\- \*\*HEALTH 502/504\*\*: cold-start Render ⇒ réessaie après 20–40s, puis Logs Render.

\- \*\*SEND 401/403\*\*: `%TOKEN%` ≠ `INTERNAL\_TOKEN` (Render) ⇒ aligne.

\- \*\*WEBHOOK 401/403\*\*: `VERIFY\_TWILIO\_SIGNATURE=true` sans signature ⇒ mets `false` pour tester, ou fais un vrai appel Twilio.



\## Coup d'œil DB (SQLite dev)



python -c "import sqlite3;con=sqlite3.connect('db/messages.db');c=con.cursor();print('rows=',c.execute('select count(\*) from messages').fetchone()\[0]);print(c.execute('select direction,text,ts from messages order by ts desc limit 3').fetchall())"





\## Twilio Sandbox

\- Webhook: `https://<service>.onrender.com/whatsapp/webhook`

\- Si rien ne revient: vérifier `/health`, l’URL exacte, et Events/Logs Render.



\## Tests d’acceptation (prod)

1\) `smoke\_prod.bat` ⇒ viser `200 / 200 / 200`

2\) Message WhatsApp reçu via `/internal/send`

3\) `diag\_prod.bat` ⇒ Reachability OK + JSON health + `CHECKIN 200` + `WEBHOOK 200`



\## Astuce sécurité

Quand prêt: `VERIFY\_TWILIO\_SIGNATURE=true` + `PUBLIC\_WEBHOOK\_URL` exact (Render). Les tests webhook “synthetic” renverront 401/403 (normal).





