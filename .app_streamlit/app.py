import streamlit as st
import json
import pandas as pd
import random
import time
import sqlite3
from datetime import datetime

# ---------- ユーザー情報入力 ----------
if "user_info_submitted" not in st.session_state:
    st.title("IQ Test for Mensa")
    st.write("Please enter your age and gender before starting. / 年齢と性別を入力してください。")

    with st.form("user_info_form"):
        age = st.number_input("Age", min_value=5, max_value=120, step=1, value=35)
        gender = st.selectbox("Gender / 性別", ["男性 / Male", "女性 / Female", "不明 / Other"], index=2)
        submitted = st.form_submit_button("Start")

        if submitted:
            st.session_state.user_info = {"age": age, "gender": gender.split("/")[1].strip()}
            st.session_state.user_info_submitted = True
            st.rerun()

# ---------- 初期化 ----------
if "user_info_submitted" not in st.session_state:
    st.stop()
if "questions" not in st.session_state:
    with open("../problems/sample_problems_Q0001_to_Q0120.json", "r") as f:
        all_problems = json.load(f)

    num_questions = min(30, len(all_problems))
    st.session_state.questions = random.sample(all_problems, k=num_questions)
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.start_time = time.time()
    st.session_state.quiz_start_time = time.time()

    # SQLite 初期化
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        age INTEGER,
        gender TEXT,
        question_id TEXT,
        selected TEXT,
        correct TEXT,
        is_correct BOOLEAN,
        time_taken FLOAT,
        score INTEGER,
        datetime TEXT
    )''')
    conn.commit()
    conn.close()

# ---------- 結果画面 ----------
if st.session_state.current >= len(st.session_state.questions):
    total_time = round(time.time() - st.session_state.quiz_start_time, 2)
    accuracy = round(100 * st.session_state.score / sum([q.get("score", 1) for q in st.session_state.questions]), 1)

    st.markdown("### 🧾 IQ Test Result Summary")
    st.write(f"✅ 正答率 / Accuracy: {accuracy}%")
    st.write(f"⏱ 所要時間 / Time taken: {int(total_time // 60)}m {int(total_time % 60)}s")
    st.markdown("""
    ---
    ### 🙏 ご協力ありがとうございました！
    ### 🙏 Thank you for your cooperation!
    """)

    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

    if st.button("🔁 Try Again", key="try_again"):
        for key in ["questions", "current", "score", "results", "start_time", "quiz_start_time", "user_info_submitted", "user_info"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.stop()

# ---------- 出題 ----------
q = st.session_state.questions[st.session_state.current]
st.markdown("### IQ Test for Mensa")
st.image(f"../problems/img/{q['image']}", use_container_width=True)
st.write("正しい図を下の画像から選んでください / Please choose the correct figure from the images below.")

elapsed_global = round(time.time() - st.session_state.quiz_start_time)
st.markdown(f"**Elapsed Time:** {elapsed_global // 60}m {elapsed_global % 60}s")

# ---------- 解答処理 ----------
def process_answer(ans):
    elapsed = round(time.time() - st.session_state.start_time, 2)
    correct = q["answer"]
    is_correct = ans == correct

    result = {
        "age": st.session_state.user_info["age"],
        "gender": st.session_state.user_info["gender"],
        "question_id": q["id"],
        "selected": ans,
        "correct": correct,
        "is_correct": is_correct,
        "time_taken": elapsed,
        "score": q.get("score", 1),
        "datetime": datetime.now().isoformat()
    }

    st.session_state.results.append(result)

    # SQLiteへ保存
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(result.values()))
    conn.commit()
    conn.close()

    st.session_state.current += 1
    st.session_state.start_time = time.time()
    st.rerun()

# ---------- 選択肢レイアウト（streamlit columns） ----------
cols_top = st.columns([1, 1, 1], gap="small")
for i, label in enumerate(["A", "B", "C"]):
    with cols_top[i]:
        st.image(f"../problems/img/{q['option_images'][label]}", width=100)
        if st.button(label, key=f"btn_{label}_{st.session_state.current}"):
            process_answer(label)

cols_bottom = st.columns([1, 1, 1], gap="small")
for i, label in enumerate(["D", "E", "F"]):
    with cols_bottom[i]:
        st.image(f"../problems/img/{q['option_images'][label]}", width=100)
        if st.button(label, key=f"btn_{label}_{st.session_state.current}"):
            process_answer(label)

# 選択肢受け取り処理
query_params = st.query_params if hasattr(st, "query_params") else {}
if "selected" in st.query_params:
    selected = st.experimental_get_query_params()["selected"][0]
    process_answer(selected)