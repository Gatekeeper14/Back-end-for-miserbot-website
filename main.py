import os
import psycopg2
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram error:", e)


def send_email(to_email, name):
    try:
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "personalizations": [{
                "to": [{"email": to_email}]
            }],
            "from": {"email": FROM_EMAIL},
            "subject": "Welcome to MiserBot 👑",
            "content": [{
                "type": "text/plain",
                "value": f"Hi {name}, you're officially on the MiserBot early access list."
            }]
        }

        requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            json=data
        )

    except Exception as e:
        print("Email error:", e)


@app.route("/", methods=["GET"])
def home():
    return "Miserbot backend is live 🚀", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔥 WEBHOOK HIT:", data)

    if not data:
        return jsonify({"status": "no data"}), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"status": "missing fields"}), 400

    print(f"📩 New Lead → {name} - {email}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO leads (name, email) VALUES (%s, %s)",
            (name, email)
        )

        conn.commit()
        cur.close()
        conn.close()

        print("✅ Lead saved to database")

        telegram_message = f"👑 New MiserBot Lead\n\nName: {name}\nEmail: {email}"

        send_telegram(telegram_message)
        send_email(email, name)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Database error:", e)
        return jsonify({"status": "database error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
