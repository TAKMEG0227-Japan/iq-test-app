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

    num_questions = min(30, len(all_problems))
    st.session_state.questions = random.sample(all_problems, k=num_questions)
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.start_time = time.time()
    st.session_state.selected = None

# ---------- 結果画面 ----------
if st.session_state.current >= len(st.session_state.questions):
    st.markdown("### 🧾 IQ Test Result Summary")
    st.write(f"\u2705 Correct Answers: {st.session_state.score} / {len(st.session_state.questions)}")

    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

    df.to_csv("logs/answers.csv", mode="a", header=False, index=False)

    if st.button("🔁 Try Again", key="try_again"):
        for key in ["questions", "current", "score", "results", "start_time", "selected"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.stop()

# ---------- 出題 ----------
q = st.session_state.questions[st.session_state.current]
st.markdown("### **IQ Test for Mensa**")
st.image(f"problems/img/{q['image']}", width=300)
st.write(q["question"])

# ---------- CSS ----------
st.markdown("""
<style>
.option-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  max-width: 330px;
  margin: auto;
}
.option-grid img {
  width: 100%;
  border-radius: 6px;
}
.option-grid form {
  margin-bottom: 0;
}
.option-grid button {
  background: none;
  border: none;
  padding: 0;
}
</style>
""", unsafe_allow_html=True)

# ---------- 解答処理 ----------
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

# ---------- HTML選択肢表示 ----------
image_html_blocks = []
for label in ["A", "B", "C", "D", "E", "F"]:
    image_url = f"problems/img/{q['option_images'][label]}"
    html = f"""
    <form action="" method="post">
        <button name="selected" value="{label}">
            <img src="{image_url}" alt="{label}">
        </button>
    </form>
    """
    image_html_blocks.append(html)

st.markdown("<div class='option-grid'>" + "".join(image_html_blocks) + "</div>", unsafe_allow_html=True)

# ---------- ボタン処理 ----------
selected_label = st.query_params.get("selected", [None])[0]
