import os
import json
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEM_JSON_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "problems", "sample_problems_Q0001_to_Q0120.json"))

def load_random_questions(num_questions=30):
    with open(PROBLEM_JSON_PATH, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    # 欠番を除く：画像と答えが両方ある問題のみ対象
  
    valid_questions = [q for q in all_questions if q.get("image") and q.get("answer")]
    print("読み込んだ問題数:", len(valid_questions))

    selected = random.sample(valid_questions, k=min(num_questions, len(valid_questions)))
    print("選ばれたID:", [q['id'] for q in selected])

    return selected




