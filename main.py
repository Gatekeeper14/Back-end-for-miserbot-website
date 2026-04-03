from flask import Flask, request, jsonify
import psycopg2
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_db():
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def home():
    return "Miserbot backend is live 🚀"


@app.route("/join", methods=["POST"])
def join():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")

        referral_code = str(uuid.uuid4())[:8]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO leads (name, email, referral_code, referrals)
            VALUES (%s, %s, %s, 0)
            RETURNING referral_code
            """,
            (name, email, referral_code),
        )

        conn.commit()

        return jsonify({
            "success": True,
            "referral_code": referral_code
        })

    except Exception as e:
        print(e)
        return jsonify({"error": "Server error"}), 500
