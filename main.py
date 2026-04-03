from flask import Flask, request, jsonify
import psycopg2
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Get database URL from Railway
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix Railway postgres URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Connect to database
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True


@app.route("/")
def home():
    return "Miserbot backend is live 🚀"


@app.route("/join", methods=["POST"])
def join():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")

        # Generate referral code
        referral_code = str(uuid.uuid4())[:8]

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO leads (name, email, referral_code, referrals)
            VALUES (%s, %s, %s, 0)
            RETURNING referral_code
            """,
            (name, email, referral_code)
        )

        conn.commit()

        return jsonify({
            "success": True,
            "referral_code": referral_code
        })

    except Exception as e:
        print(e)
        return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
