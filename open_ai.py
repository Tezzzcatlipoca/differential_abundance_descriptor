from openai import OpenAI
import pandas as pd
import os
import time
import datetime
import json
from CONSTANTS import *


def convert_file_to_json(txt_file_path: str) -> str:
    assert ".csv" not in txt_file_path, "Data file should be Tab-separated!"
    try:
        df = pd.read_csv(txt_file_path, sep="\t", encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: CSV file not found at {txt_file_path}")
        return None
    data_dict = df.to_dict(orient='records')
    json_data = json.dumps(data_dict)
    time.sleep(1)
    return str(json_data)


def ingest_file(txt_file_path: str) -> str:
    if ".txt" in txt_file_path:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            data = file.read()
    else:
        data = convert_file_to_json(txt_file_path)
    return data


def query_openai(question: str, data_file: str = '', tmax_tokens=MAX_TOKENS, temperature=0.3, model_version: str="gpt-3.5-turbo-0125"):
    assert question != "", "Empty question to the model!"
    if model_version == "":
        model_version = "gpt-3.5-turbo-0125"
    #if tmax_tokens > 14096:
    #    print("Model's max number of tokens is 4096! Truncating")
    #    tmax_tokens = 4096
    api_key = os.environ['OPENAI_KEY']
    client = OpenAI(api_key=api_key)
    if data_file != '':
        table = ingest_file(data_file)
    else:
        table = ''
    prompt = f"{question}\n\n{table}"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user", "content": prompt
            }
        ],
        model=model_version,
        #model="gpt-4",
        #model="gpt-4-32k",
        max_tokens=tmax_tokens,
        temperature=temperature
    )
    time.sleep(AI_WAIT_TIME)
    print(chat_completion.choices[0].message.content)
    with open(os.path.join(LOGS_PATH, OPENAI_LOG_FILE), 'a', encoding='utf-8') as f:
        f.write(str(datetime.datetime.now())+'\n')
        f.write(str(chat_completion)+'\n\n')
    return chat_completion.choices[0].message.content


