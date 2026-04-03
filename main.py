from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

def get_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            dbname=os.getenv("PGDATABASE")
        )
        return conn
    except Exception as e:
        print("❌ DB connection error:", e)
        return None


@app.route("/", methods=["GET"])
def home():
    return "Miserbot backend is live 🚀", 200


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    data = request.json if request.method == "POST" else request.args

    print("🔥 WEBHOOK HIT:", data)

    if data and "email" in data:

        name = data.get("name", "unknown")
        email = data.get("email")

        print(f"📩 New Lead → Name: {name}, Email: {email}")

        conn = get_db()

        if conn:
            try:
                cur = conn.cursor()

                cur.execute(
                    "INSERT INTO leads (email, created_at) VALUES (%s, NOW())",
                    (email,)
                )

                conn.commit()

                cur.close()
                conn.close()

                print("✅ Lead saved")

            except Exception as e:
                print("❌ DB ERROR:", e)

        return jsonify({"status": "success"}), 200


    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
