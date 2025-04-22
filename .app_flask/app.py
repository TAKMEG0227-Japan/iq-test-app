from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret-key"

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEM_JSON_PATH = os.path.join(BASE_DIR, "../problems/sample_problems_Q0001_to_Q0120.json")
IMG_DIR = os.path.join(BASE_DIR, "../problems/img")
DB_PATH = os.path.join(BASE_DIR, "db/results.db")

# カスタム静的ファイル（画像）
@app.route('/static/img/<path:filename>')
def custom_static(filename):
    return send_from_directory(IMG_DIR, filename)

# 問題読み込み
def load_random_questions(n=30):
    with open(PROBLEM_JSON_PATH, "r", encoding="utf-8") as f:
        all_problems = json.load(f)
    valid_questions = [q for q in all_problems if os.path.exists(os.path.join(IMG_DIR, q["image"]))]
    selected = random.sample(valid_questions, k=n)
    print("読み込んだ問題数:", len(valid_questions))
    print("選ばれたID:", [q["id"] for q in selected])
    return selected

# トップページ（初期入力）
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    session.clear()
    session["age"] = request.form.get("age", "35")
    session["gender"] = request.form.get("gender", "other")
    session["questions"] = load_random_questions()
    session["start_time"] = datetime.now().isoformat()
    session["total_questions"] = len(session["questions"])
    return redirect(url_for("question", qnum=1))

# 問題ページ
@app.route("/question/<int:qnum>")
def question(qnum):
    questions = session.get("questions", [])
    if not questions or qnum < 1 or qnum > len(questions):
        return redirect(url_for("result"))

    q = questions[qnum - 1]
    return render_template("question.html", qnum=qnum, q=q)

# 解答送信ページ
@app.route("/submit/<int:qnum>", methods=["POST"])
def submit(qnum):
    selected = request.form.get("selected")
    questions = session.get("questions", [])
    if not questions or qnum > len(questions):
        return redirect(url_for("index"))

    q = questions[qnum - 1]
    correct = q.get("answer")
    is_correct = selected == correct

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        age TEXT, gender TEXT, question_id TEXT,
        selected TEXT, correct TEXT, is_correct INTEGER, datetime TEXT)''')
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session.get("age"), session.get("gender"), q["id"], selected, correct, int(is_correct), datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return redirect(url_for("question", qnum=qnum+1))

# 結果ページ
@app.route("/result")
def result():
    start_time = datetime.fromisoformat(session.get("start_time"))
    end_time = datetime.now()
    elapsed = end_time - start_time
    minutes = elapsed.seconds // 60
    seconds = elapsed.seconds % 60

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(is_correct) FROM results WHERE datetime >= ?", (session["start_time"],))
    total, correct = c.fetchone()
    conn.close()

    accuracy = round(100 * correct / total, 1) if total else 0
    return render_template("result.html", accuracy=accuracy, minutes=minutes, seconds=seconds)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)