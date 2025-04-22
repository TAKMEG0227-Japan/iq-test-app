from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os
from datetime import datetime
from utils.problem_loader import load_random_questions

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super_secret_12345"

# 静的ファイルとして img を提供（problems/img/）
@app.route('/img/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'problems', 'img'), filename)

# トップページ：年齢・性別の入力
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        age = request.form["age"]
        gender = request.form["gender"]
        session["age"] = age
        session["gender"] = gender
        session.pop("questions", None)  # セッション初期化（←追加）
        return redirect(url_for("question", qnum=1))
    return render_template("index.html")

# 問題ページ
@app.route("/question/<int:qnum>")
def question(qnum):
    if "questions" not in session:
        session["questions"] = load_random_questions()
        session["start_time"] = datetime.now().isoformat()

    questions = session["questions"]
    if qnum > len(questions):
        return redirect(url_for("result"))

    q = questions[qnum - 1]
    return render_template("question.html", qnum=qnum, q=q)

# 解答送信ページ
@app.route("/submit/<int:qnum>", methods=["POST"])
def submit(qnum):
    selected = request.form.get("selected")
    age = session.get("age")
    gender = session.get("gender")
    questions = session.get("questions", [])
    q = questions[qnum - 1] if qnum - 1 < len(questions) else None
    correct = q["answer"] if q else None
    is_correct = selected == correct

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "db", "results.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            age INTEGER,
            gender TEXT,
            question_id TEXT,
            selected TEXT,
            correct TEXT,
            is_correct BOOLEAN,
            datetime TEXT
        )
    """)
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?)",
              (age, gender, q["id"], selected, correct, is_correct, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return redirect(url_for("question", qnum=qnum + 1))

# 結果ページ
@app.route("/result")
def result():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "db", "results.db")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY datetime DESC LIMIT 30")
    results = c.fetchall()
    conn.close()
    return render_template("result.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
