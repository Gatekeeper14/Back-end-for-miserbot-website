import os
import psycopg2
import requests
import openai

from flask import Flask, request, jsonify
from flask_cors import CORS

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def save_lead(name, email):

    if not DATABASE_URL:
        print("No database configured")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO leads (name,email) VALUES (%s,%s)",
        (name, email)
    )

    conn.commit()
    cur.close()
    conn.close()


def send_email(name, email):

    if not SENDGRID_API_KEY:
        print("SendGrid not configured")
        return

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email,
        subject="Welcome to MiserBot 👑",
        html_content=f"""
        <strong>Hello {name},</strong><br><br>
        You're officially inside MiserBot.<br><br>
        We'll be contacting you soon.<br><br>
        👑
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("Email sent")

    except Exception as e:
        print("Email error:", e)


def send_telegram(message):

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:

        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
        )

        print("Telegram alert sent")

    except Exception as e:
        print("Telegram error:", e)


def analyze_lead(name, email):

    if not OPENAI_API_KEY:
        return "AI not configured"

    try:

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Analyze this lead.

Name: {name}
Email: {email}

Return a short summary and score the lead LOW, MEDIUM, or HIGH.
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"AI error: {e}"


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

        save_lead(name, email)

        send_email(name, email)

        ai_summary = analyze_lead(name, email)

        send_telegram(
            f"""
👑 New MiserBot Lead

Name: {name}
Email: {email}

AI Analysis:
{ai_summary}
"""
        )

        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 3000))

    app.run(host="0.0.0.0", port=port)
