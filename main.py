from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

def get_db():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL is missing")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(db_url)


@app.route("/", methods=["GET"])
def home():
    return "Miserbot backend is live 🚀", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔥 WEBHOOK HIT:", data)

    # WEBSITE FORM HANDLER
    if data and "email" in data and "name" in data:
        name = data.get("name")
        email = data.get("email")
        source = data.get("source", "website")

        print(f"📩 New Lead → Name: {name}, Email: {email}, Source: {source}")

        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO leads (name, email, referrals) VALUES (%s,%s,0)",
                (name, email)
            )

            conn.commit()
            cur.close()
            conn.close()

            print("✅ Lead saved to database")

        except Exception as e:
            print("❌ DB ERROR:", e)

        return jsonify({
            "status": "success",
            "message": "Lead received"
        }), 200


    # TELEGRAM HANDLER
    message = data.get("message", {}) if data else {}
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if chat_id:
        print(f"📲 Telegram → {chat_id}: {text}")

    return jsonify({
        "status": "ok"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
