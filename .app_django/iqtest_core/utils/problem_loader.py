import json
import os
import random

def load_random_questions(n=30):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    problems_path = os.path.join(base_dir, '../../../problems/sample_problems_Q0001_to_Q0120.json')
    with open(problems_path, encoding='utf-8') as f:
        problems = json.load(f)
    random.shuffle(problems)
    return problems[:n]