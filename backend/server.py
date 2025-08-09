from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = "data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    referred_by INTEGER
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS withdraws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    method TEXT,
                    status TEXT DEFAULT 'pending'
                )""")
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, balance, referred_by FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, referred_by=None):
    if not get_user(user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (?, ?, ?)",
                  (user_id, 0, referred_by))
        conn.commit()
        conn.close()

@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    user = get_user(user_id)
    if not user:
        add_user(user_id)
        user = get_user(user_id)
    return jsonify({"balance": user[1]})

@app.route("/api/reward", methods=["POST"])
def reward():
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount", 0)
    if not user_id or amount <= 0:
        return jsonify({"error": "invalid request"}), 400
    add_user(user_id)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

    # Bonus referral 10% kalau ada
    c.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
    ref = c.fetchone()
    if ref and ref[0]:
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (int(amount * 0.1), ref[0]))
        conn.commit()

    conn.close()
    return jsonify({"success": True})

@app.route("/api/withdraw", methods=["POST"])
def withdraw():
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount")
    method = data.get("method")
    if not user_id or not amount or not method:
        return jsonify({"error": "invalid request"}), 400
    user = get_user(user_id)
    if not user or user[1] < amount:
        return jsonify({"error": "saldo tidak cukup"}), 400
    if amount < 1000:
        return jsonify({"error": "minimal penarikan 10000 koin"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    c.execute("INSERT INTO withdraws (user_id, amount, method) VALUES (?, ?, ?)", (user_id, amount, method))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/")
def home():
    return "API berjalan!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
