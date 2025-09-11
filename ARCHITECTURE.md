\# Architecture — Companion Factory (Render Free + Twilio Sandbox)



\## Flux (vue d'ensemble)

Utilisateur WhatsApp

→ Twilio Sandbox

→ \*\*Flask\*\* `/whatsapp/webhook` (POST form-urlencoded)

&nbsp;  → Gardes-fous: idempotence \*\*MessageSid\*\*, mini rate-limit (par user), (option) signature HMAC Twilio

&nbsp;  → Mémoire: SQLite (dev) / Postgres (prod) — historique ~16 msgs

&nbsp;  → \*\*LLM\*\*: wrappers `safe\_\*` vers gpt-4o-mini (timeout=15s, retries=2, fallback)

&nbsp;  ← Réponse texte courte

← Twilio envoie au user WhatsApp



\## Composants clés

\- \*\*Webhook Flask\*\*: routes `/whatsapp/webhook`, `/health`, `/internal/\*`

\- \*\*DB\*\*: table `messages` (msg\_sid unique, direction, text, ts, user\_id)

\- \*\*Logs\*\*: JSON (event, status, latency, req\_id, DB/LLM errors)

\- \*\*Internal\*\*: `/internal/send` (envoi test), `/internal/checkin` (dry\_run OK)



\## Render Free — notes

\- Spindown possible ⇒ 1er hit plus lent (cold-start).

\- Pour éviter les timeouts Twilio: option \*\*async léger\*\* (thread/executor) qui renvoie `200` instant.



\## ENV (référence)

OPENAI\_API\_KEY, INTERNAL\_TOKEN, TWILIO\_ACCOUNT\_SID, TWILIO\_AUTH\_TOKEN,

TWILIO\_SANDBOX\_FROM, USER\_WHATSAPP\_TO, VERIFY\_TWILIO\_SIGNATURE,

PUBLIC\_WEBHOOK\_URL, RATE\_LIMIT\_SECONDS, WEATHER\_SUMMARY, PYTHON\_VERSION



