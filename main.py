from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)


def get_db():
    db_url = os.getenv("DATABASE_URL")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(db_url)


@app.route("/", methods=["GET"])
def home():
    return "Miserbot backend is live 🚀", 200


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


@app.route("/webhook", methods=["POST","GET"])
def webhook():

    data = request.json if request.method == "POST" else request.args

    print("🔥 WEBHOOK HIT:", data)

    if data and "email" in data:

        name = data.get("name","unknown")
        email = data.get("email")
        source = data.get("source","website")

        print(f"📩 New Lead → Name: {name}, Email: {email}, Source: {source}")

        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO leads (email,created_at,referrals) VALUES (%s,NOW(),0)",
                (email,)
            )

            conn.commit()
            cur.close()
            conn.close()

            print("✅ Lead saved")

        except Exception as e:
            print("❌ DB ERROR:", e)

        return jsonify({"status":"success"}),200

    return jsonify({"status":"ok"}),200


if __name__ == "__main__":
    port = int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0", port=port)
