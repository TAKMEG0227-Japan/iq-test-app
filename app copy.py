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

    num_questions = min(30, len(all_problems))  # ← 出題数はここで調整
    st.session_state.questions = random.sample(all_problems, k=num_questions)
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.start_time = time.time()
    st.session_state.selected = None  # 選択肢追跡用

# ---------- 結果画面 ----------
if st.session_state.current >= len(st.session_state.questions):
    st.markdown("### 🧾 IQ Test Result Summary")
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
st.markdown("### **IQ Test for Mensa**")
st.image(f"problems/img/{q['image']}", width=300)
st.write(q["question"])

# ---------- グリッド選択肢レイアウト（画像つき + 自動送信） ----------
def process_answer(ans):
    elapsed = round(time.time() - st.session_state.start_time, 2)
    correct = q["answer"]
    is_correct = ans == correct

    if is_correct:
        st.session_state.score += q.get("score", 1)

    st.session_state.results.append({
        "question_id": q["id"],
        "selected": ans,
        "correct": correct,
        "is_correct": is_correct,
        "time_taken": elapsed,
        "score": q.get("score", 1),
        "datetime": datetime.now().isoformat()
    })

    st.session_state.current += 1
    st.session_state.start_time = time.time()
    st.session_state.pop("selected", None)
    st.rerun()

with st.container():
    cols_top = st.columns([1, 1, 1], gap="small")
    for i, label in enumerate(["A", "B", "C"]):
        with cols_top[i]:
            st.image(f"problems/img/{q['option_images'][label]}", width=100)
            if st.button(label, key=f"btn_{label}_{st.session_state.current}"):
                st.session_state.selected = label
                process_answer(label)

    cols_bottom = st.columns([1, 1, 1], gap="small")
    for i, label in enumerate(["D", "E", "F"]):
        with cols_bottom[i]:
            st.image(f"problems/img/{q['option_images'][label]}", width=100)
            if st.button(label, key=f"btn_{label}_{st.session_state.current}"):
                st.session_state.selected = label
                process_answer(label)
