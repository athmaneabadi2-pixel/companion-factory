from flask import Flask, request, jsonify, Response
import os, html, logging

# --- App ---
app = Flask(__name__)
log = app.logger

# --- Health (pour Render) ---
@app.get("/health")
def health():
    return jsonify(status="ok"), 200

# --- Internal send (utilisé par les tests + monitoring) ---
@app.post("/internal/send")
def internal_send():
    token_expected = os.getenv("INTERNAL_TOKEN", "dev-123")
    token = request.headers.get("X-Token", "")
    if token != token_expected:
        return jsonify(error="unauthorized"), 401

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    reply = f"echo: {text}" if text else "echo: (vide)"
    return jsonify(reply=reply), 200

# --- Twilio helpers ---
def _twiml_text(message: str) -> Response:
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{html.escape(message)}</Message></Response>'
    return Response(twiml, content_type="application/xml")

# LLM (OpenAI optionnel) — fallback = echo
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

def llm_reply(user_text: str) -> str:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or OpenAI is None:
        return f"Echo: {user_text}"

    try:
        client = OpenAI(api_key=key)
        sys_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "Tu es un compagnon chaleureux et concis. Réponds en une phrase."
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_text or "Dis bonjour."},
            ],
            max_tokens=120,
            temperature=0.6,
        )
        content = (resp.choices[0].message.content or "").strip()
        return content or f"Echo: {user_text}"
    except Exception as e:
        log.exception("LLM error")
        return f"Echo: {user_text}"

# --- Webhook principal Twilio (WhatsApp/SMS) ---
@app.post("/twilio/inbound")
def twilio_inbound():
    body = (request.form.get("Body") or "").strip()
    reply = llm_reply(body) if body else "👋 Dis-moi quelque chose."
    return _twiml_text(reply)

# --- Alias pour anciennes configs (évite 404) ---
@app.post("/whatsapp/webhook")
def whatsapp_webhook():
    return twilio_inbound()

# --- Run local (utile en dev ; ignoré par gunicorn sur Render) ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
