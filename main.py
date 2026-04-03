import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "Miserbot backend is live 🚀", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔥 WEBHOOK HIT:", data)

    if data and "email" in data and "name" in data:
        name = data.get("name")
        email = data.get("email")

        print(f"📩 New Lead → {name} - {email}")

        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
