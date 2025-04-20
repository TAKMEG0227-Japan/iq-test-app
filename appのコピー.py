import streamlit as st
import json
import pandas as pd
import random
import time
from datetime import datetime

# ---------- 初期化 ----------
if "questions" not in st.session_state:
    with open("problems/sample_problems.json", "r") as f:
        all_problems = json.load(f)

    num_questions = min(10, len(all_problems))  # ← 必要に応じて 30 に変更
    st.session_state.questions = random.sample(all_problems, k=num_questions)
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.start_time = time.time()
    st.session_state.selected = None  # 選択肢追跡用

# ---------- 結果画面 ----------
if st.session_state.current >= len(st.session_state.questions):
    st.title("\U0001F9FE Result Summary")
    st.write(f"\u2705 Correct Answers: {st.session_state.score} / {len(st.session_state.questions)}")

    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

    # CSV保存
    df.to_csv("logs/answers.csv", mode="a", header=False, index=False)

    if st.button("🔁 Try Again", key="try_again"):
        for key in ["questions", "current", "score", "results", "start_time", "selected"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.stop()

# ---------- 問題出題 ----------
q = st.session_state.questions[st.session_state.current]
st.title(f"\U0001F9E0 IQ Test - Question {st.session_state.current + 1} of {len(st.session_state.questions)}")
st.image(f"problems/img/{q['image']}", use_container_width=True)
st.write(q["question"])

# ---------- グリッド選択肢レイアウト ----------
cols_top = st.columns(3)
cols_bottom = st.columns(3)

# 選択肢ボタン表示
for i, label in enumerate(["A", "B", "C"]):
    if cols_top[i].button(label, key=f"btn_{label}_{st.session_state.current}"):
        st.session_state.selected = label

for i, label in enumerate(["D", "E", "F"]):
    if cols_bottom[i].button(label, key=f"btn_{label}_{st.session_state.current}"):
        st.session_state.selected = label

# ---------- Submit処理 ----------
answer = st.session_state.get("selected", None)
if answer is not None:
    st.markdown(f"\u2705 Selected: **{answer}**")

    if st.button("Submit Answer", key=f"submit_btn_{st.session_state.current}"):
        elapsed = round(time.time() - st.session_state.start_time, 2)
        correct = q["answer"]
        is_correct = answer == correct

        if is_correct:
            st.session_state.score += 1

        st.session_state.results.append({
            "question_id": q["id"],
            "selected": answer,
            "correct": correct,
            "is_correct": is_correct,
            "time_taken": elapsed,
            "datetime": datetime.now().isoformat()
        })

        st.session_state.current += 1
        st.session_state.start_time = time.time()
        st.session_state.pop("selected", None)
        st.rerun()
