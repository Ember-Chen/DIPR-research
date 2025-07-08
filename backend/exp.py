import pandas as pd
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from agent import get_ans_normal, get_ans
import re
from utils import call_llm

# 用于存储每个 model 的结果
lock = threading.Lock()  # 保证写入字典时的线程安全

def process_question(question_id, question, model):
    """处理单个问题，带重试机制"""
    MAX_TRY = 3 # 最大尝试次数
    for attempt in range(MAX_TRY):
        try:
            res = get_ans(question, model)
            return res
        except Exception as e:
            print(f"Error with question {question_id} using {model} on attempt {attempt+1}: {e}")
    return "ERROR"  # 多次失败，记录错误


def process_question_normal(question_id, question, model):
    """处理单个问题，带重试机制"""
    MAX_TRY = 3  # 最大尝试次数
    for attempt in range(MAX_TRY):
        try:
            res = get_ans_normal(question, model)
            return res
        except Exception as e:
            print(f"Error with question {question_id} using {model} on attempt {attempt+1}: {e}")
    return "ERROR"  # 多次失败，记录错误


def get_pred(dataset_csv, model, start, end):
    df = pd.read_csv(dataset_csv)
    df = df[start:end]  # 只处理指定范围内的问题

    """为单个 model 处理所有问题"""
    local_results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(process_question, row['id'], row['Prompt'], model): row['id']
            for _, row in df.iterrows()
        }
        for future in as_completed(futures):
            question_id = futures[future]
            ans = future.result()
            with lock:
                local_results[question_id] = ans

    # 写入JSON文件
    with open(f"./output_raw_FRAMES/{model}_s{start}_e{end}.json", "w", encoding="utf-8") as f:
        json.dump(local_results, f, ensure_ascii=False, indent=2)


def eval_ans(gt, pred, eval_model):
    """评估答案的正确性"""
    prompt = prompt = f"""
        You are an AI judge for evaluating answers. Your task is to determine whether the predicted answer correctly matches the ground truth in meaning, using a *loose and tolerant* standard.

        Important Instructions:
        - Focus on whether the *main meaning* of the predicted answer matches the ground truth.
        - Accept answers that are *semantically similar* or *express the same core idea*, even if the wording is different.
        - Ignore minor differences in wording, grammar, or phrasing.
        - Be generous in your evaluation. If the meaning is roughly correct, consider it correct.

        Output Instructions:
        - Only output either "true" or "false", wrapped inside <decision></decision> tags.
        - Do not explain anything. Do not output anything else beyond the decision in the tags.

        Ground Truth: {gt}
        Predicted Answer: {pred}
    """

    raw_ret = call_llm(prompt, eval_model).strip()
    flag = re.search(r'<decision>(.*?)</decision>', raw_ret).group(1).strip()
    return flag


def proc_json(filepath, dataset_csv):
    """评估JSON文件中的答案"""
    df = pd.read_csv(dataset_csv)
    json_arr = []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    for question_id, pred in data.items():
        print(f"Evaluating question {question_id} with prediction: {pred}")
        gt = df[df['id'] == int(question_id)]['Answer'].values[0]
        is_correct = eval_ans(gt, pred, 'gpt-4o')
        json_arr.append({
            "question_id": question_id,
            "ground_truth": gt,
            "predicted_answer": pred,
            "is_correct": is_correct
        })
    with open(f"eval{filepath}", "w", encoding="utf-8") as f:
        json.dump(json_arr, f, ensure_ascii=False, indent=2)
