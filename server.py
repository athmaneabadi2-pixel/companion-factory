from flask import Flask, request, jsonify
from dotenv import load_dotenv; load_dotenv()
import os
app = Flask(__name__)
@app.get("/health")
def health(): return jsonify(status="ok"), 200
@app.post("/internal/send")
def internal_send():
    expected = os.getenv("INTERNAL_TOKEN", "dev-123")
    if request.headers.get("X-Token","") != expected: return jsonify(error="forbidden"), 403
    if request.args.get("format")=="text":
        data = request.get_json(silent=True) or {}
        return (data.get("text",""), 200, {"Content-Type":"text/plain; charset=utf-8"})
    return jsonify(ok=True), 200
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
