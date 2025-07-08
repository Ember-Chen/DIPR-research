from dotenv import load_dotenv
import os
import re
from openai import OpenAI
import requests
from langchain_text_splitters import MarkdownHeaderTextSplitter
import ollama

load_dotenv()

MAX_RETRY = 3  # Maximum number of retries for getting a valid answer

MODEL = "deepseek-r1-0528"

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

JINA_API_KEY = os.getenv("JINA_API_KEY")

ZILLIZ_URL = os.getenv("ZILLIZ_URL")
ZILLIZ_API_KEY = os.getenv("ZILLIZ_API_KEY")

EXAMPLE_Q = "I have an element in mind and would like you to identify the person it was named after. Here's a clue: The element's atomic number is 9 higher than that of an element discovered by the scientist who discovered Zirconium in the same year."

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def call_llm(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    # print(response.choices[0].message.content)
    print("---------------START CALLING----------------")
    print(f"calling LLM with prompt:\n{prompt}")
    print(f"LLM response:\n{response.choices[0].message.content}")
    print("----------------END CALLING----------------")
    return response.choices[0].message.content


def call_jina_search(query):
    url = "https://s.jina.ai/"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "X-Respond-With": "no-content"
    }
    params = {
        "q": query
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        # 只保留content的前n行
        content = response.text.strip()
        content_lines = content.splitlines()[:7]
        content = '\n'.join(content_lines)
        # 去除url
        content = re.sub(r'https?://\S+', '', content)
        return content
    else:
        print("请求失败，状态码:", response.status_code)
        print(response.text)
        return None


def call_jina_reader(url):
    url = f"https://r.jina.ai/{url}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        print("请求失败，状态码:", response.status_code)
        print(response.text)
        return None



########################## embed相关 ################################
def preprocess_txt(content):
    # 1 将标题替换为 Markdown 格式
    content = re.sub(r'^(.*?)\n[-]{2,}$', r'## \1', content, flags=re.MULTILINE)

    # 2 去除链接
    content = re.sub(r'\(https?://[^\)]*\)', '', content)

    return content


def split_text(content) -> list:
    # 指定要分割的标题
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    md_header_splits = markdown_splitter.split_text(content)

    res_list = [md_header_splits[i].page_content for i in range(len(md_header_splits))]

    return res_list


def call_embed_model(prompt):
    res = ollama.embeddings(model='jina/jina-embeddings-v2-base-de', prompt='Wie ist das Wetter heute?')
    return res.embedding


########################## db 相关 ################################
def db_insert(doc, collection_name):
    vector = call_embed_model(doc)
    
    payload = {
        "collectionName": collection_name,
        "doc": doc,
        "vector": vector
    }

    headers = {
        "Authorization": "Bearer " + ZILLIZ_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(ZILLIZ_URL + "/insert", json=payload, headers=headers)

    print(response.json())
    return response.json()


def db_search(doc, collection_name):
    vector_data = call_embed_model(doc)  # 假设返回 list
    payload = {
        "collectionName": collection_name,
        "data": [vector_data],
        "limit": 10,
        "outputFields": ["doc", "distance", "id"]
    }

    headers = {
        "Authorization": f"Bearer {ZILLIZ_API_KEY}",
        "Accept": "application/json"
    }

    response = requests.post(f"{ZILLIZ_URL}/search", json=payload, headers=headers)
    
    print(response.json())
    return response.json()


if __name__ == '__main__':
    res = call_jina_search(EXAMPLE_Q)
    print(res)

    res = call_jina_reader("https://jina.ai/blog/2023-10-09-jina-ai-llm/")