# --- haut de fichier ---
from flask import Flask, request, jsonify, Response
import os, html, logging

# LLM (OpenAI) optionnel
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

app = Flask(__name__)
log = app.logger

# --- endpoints existants /health, /internal/send ... ---

def _twiml_text(message: str) -> Response:
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{html.escape(message)}</Message></Response>'
    return Response(twiml, content_type="application/xml")

def llm_reply(user_text: str) -> str:
    """Réponse LLM courte et chaleureuse. Fallback -> echo si erreur/clé absente."""
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or OpenAI is None:
        return f"Echo: {user_text}"
    try:
        client = OpenAI(api_key=key)
        sys_prompt = os.getenv("SYSTEM_PROMPT", "Tu es un compagnon chaleureux et concis. Réponds en une phrase.")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_text or "Dis bonjour."},
            ],
            max_tokens=120,
            temperature=0.6,
        )
        return (resp.choices[0].message.content or "").strip() or f"Echo: {user_text}"
    except Exception as e:
        log.exception("LLM error")
        return f"Echo: {user_text}"

@app.post("/twilio/inbound")
def twilio_inbound():
    body = (request.form.get("Body") or "").strip()
    reply = llm_reply(body) if body else "👋 Dis-moi quelque chose."
    return _twiml_text(reply)

# Alias pour anciennes configs Twilio
@app.post("/whatsapp/webhook")
def whatsapp_webhook():
    return twilio_inbound()
