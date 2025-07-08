from utils import call_llm, db_search, call_jina_search, EXAMPLE_Q, MODEL, MAX_RETRY
import re

def split_task(question, model)->list:
    '''1 分解任务'''
    prompt = f"""
        You are an AI assistant specialized in decomposing complex questions into clear sub-questions for independent information search tasks.
        Your task:
        - Read the user's question carefully.
        - Break down the question into multiple minimal, focused search sub-tasks.
        - Each sub-task should correspond to a single, specific fact-finding goal that can be searched independently.
        - The sub-questions must strictly follow the logical order required to solve the original question step by step.
        - Present the sub-tasks, with no additional explanation or answers. Each sub-task should be prefixed with a tag: <sub_q></sub_q>. Must in a pair of tag!
        - Do not answer the sub-questions. Only list them. Only return the sub-tasks, one per line, without any additional text or formatting.
        Here is the question:
        {question}
    """
    raw_res = call_llm(prompt, model)

    sub_qs = re.findall(r'<sub_q>(.*?)</sub_q>', raw_res, flags=re.DOTALL)

    return sub_qs


def do_sub_q(sub_q, preinfo, model):
    '''2 执行子任务'''
    prompt = f"""
        We have the following known information: {preinfo if preinfo else 'None'}.
        Now, here is the question: {sub_q}

        Please carefully analyze the question and provide *only one line* as your output, wrapped in the appropriate tags based on the following instructions:

        1. If you can confidently infer a clear and definitive answer based on the provided information and reasoning, simply return the answer wrapped within <answer> and </answer> tags.
        2. If the answer is extremly hard and you are truly uncertain, return the recommended query keywords wrapped within <query_db> and </query_db> tags.
        3. If the question is highly time-sensitive or requires the latest online information (e.g., today's date, current weather), return the recommended search keywords wrapped within <query_ol> and </query_ol> tags.

        Do not include any explanations or additional text. Only return the single line of output within the correct tags.
    """

    raw_ret = call_llm(prompt, model).strip()

    # 正则匹配三种情况
    answer_match = re.search(r'<answer>(.*?)</answer>', raw_ret)
    query_db_match = re.search(r'<query_db>(.*?)</query_db>', raw_ret)
    query_ol_match = re.search(r'<query_ol>(.*?)</query_ol>', raw_ret)

    if answer_match:
        # 1 直接回答
        ans = answer_match.group(1).strip()
        return ans

    elif query_db_match:
        # 2 数据库查询
        print(f"Database query needed for sub-question: {sub_q}")
        q_db = query_db_match.group(1).strip()
        db_info = db_search(q_db, "wiki")
        prompt_2 = f"""
            - The original question is: {sub_q}
            - We have the following known information: {preinfo if preinfo else 'None'}.
            - Based on the database search results: {db_info}, please provide a final answer to the original question.
            - Remember to only return the final answer, without any additional text or explanation.
        """

        ans = call_llm(prompt_2, model).strip()
        return ans

    elif query_ol_match:
        # 3 在线查询
        print(f"Online search needed for sub-question: {sub_q}")
        q_ol = query_ol_match.group(1).strip()
        ol_info = call_jina_search(q_ol)
        prompt_2 = f"""
            - The original question is: {sub_q}
            - We have the following known information: {preinfo if preinfo else 'None'}.
            - Based on the online search results: {ol_info}, please provide a final answer to the original question.
            - Remember to only return the final answer, without any additional text or explanation.
        """

        ans = call_llm(prompt_2, model).strip()
        return ans

    else:
        # 4 fallback（异常情况，可选日志或报错处理）
        print(f"Unexpected response format: {raw_ret}")
        return "no answer"


def summarize(question, preinfo, model):
    '''3 汇总答案'''
    prompt = f"""
        1.Now we know the following information: {'; '.join(preinfo)}.
        2.Based on this information, please provide a final answer to the original question: {question} \n
        3.Remember to only return the final answer, without any additional text or explanation. Only return the answer it self. No json format.
    """
    final_ans = call_llm(prompt, model).strip()
    return final_ans


def assess(question, preinfo, model):
    '''4 反思评估'''
    prompt = f"""
        - The original question is: {question}
        - We have the following chain of thoughts: {'; '.join(preinfo)}.
        - Please assess the correctness of the chain of thoughts and the final answer.
        - If the chain of thoughts is correct and leads to a valid answer, return 1. Only return the assessment result, without any additional text or explanation.
        - Else thoroughly analyze the logical errors in the chain of thoughts.
    """
    
    assessment = call_llm(prompt, model).strip()

    print(f"Assessment result: {assessment}")

    return assessment


def get_ans(question, model):
    # 1 分解任务
    print("========================= 1 Splitting the question into sub-tasks... =========================")
    sub_qs = split_task(question, model)
    sub_qs_w_anss = [None] * len(sub_qs)  # 用于存储子任务的答案
    
    preinfo = [None] * len(sub_qs)

    # 2 do sub_qs
    print("========================= 2 Processing sub-tasks... =========================")
    for id in range(0, len(sub_qs)):
        sub_q = sub_qs[id] # 子任务的描述

        print(f'Processing sub_q {id}: {sub_q}')

        ans = do_sub_q(sub_q, preinfo, model)

        sub_qs_w_anss[id] = {
            "sub_q": sub_q,
            "sub_ans": ans
        }

        preinfo[id] = f"{sub_q}: {ans}"

    # 3 sum
    print("========================= 3 Summarizing the final answer... =========================")
    final_ans = summarize(question, preinfo, model)

    response = {
        "question": question,
        "sub_qs_w_anss": sub_qs_w_anss,
        "final_ans": final_ans
    }

    return response


def get_ans_normal(question, model):
    '''直接回答问题'''
    prompt = f"""
        You are an AI assistant. Please carefully analyze the following question and provide the answer.  
        Important: Only output the answer itself, and wrap your answer with <ans></ans> tags.  
        Do not explain anything. Do not output anything else beyond the answer in the tags.

        Question: {question}
    """
    raw_ret = call_llm(prompt, model).strip()
    raw_ret = re.sub(r'> search\((.*?)\)', '', raw_ret, flags=re.DOTALL) # 防止gpt-4o搜索的结果干扰tag提取

    final_ans = re.search(r'<ans>(.*?)</ans>', raw_ret).group(1).strip()
    
    return final_ans


if __name__ == '__main__':
    ans = get_ans(EXAMPLE_Q, MODEL)
    print(f"FINAL++++++++++++++++++++++++\n{ans}")