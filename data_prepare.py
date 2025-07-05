from utils import call_jina_reader, preprocess_txt, split_text, db_insert
import pandas as pd
import time


def proc_one_url(url, collection_name):
    # 1. 查询网页
    raw_txt = call_jina_reader(url)
    raw_txt = preprocess_txt(raw_txt)

    # 2. 分段
    segments = split_text(raw_txt)

    for i, seg in enumerate(segments):
        # 3. 写入数据库
        print(f"Inserting segment {i+1}/{len(segments)} into database...")
        # print(seg)
        db_insert(seg, collection_name)

    print("=========DONE=========")


def gather_urls(file_path):
    df = pd.read_csv(file_path)
    urls_1 = df['wikipedia_link_1'].dropna().tolist()
    urls_2 = df['wikipedia_link_2'].dropna().tolist()

    urls = list(set(urls_1 + urls_2))  # 去重
    
    with open('urls.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')


def proc_n_urls(file_path, collection_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = f.readlines()

        for i, url in enumerate(urls):
            url = url.strip()
            if url:
                print(f"Processing URL: {url}")
                proc_one_url(url, collection_name)
            else:
                print("Empty URL, skipping...")
            if (i + 1) % 20 == 0:
                print(f"Processed {i + 1} URLs, sleeping for 60 seconds...")
                time.sleep(60)