from openai import OpenAI
import pandas as pd
import os
import time
import datetime
import json

OPENAI_LOG_FILE = 'openai_log.txt'
DATA_FILE = "differential_genera_input.txt"
ABSTRACT = "Recently, the potential role of gut microbiome in metabolic diseases has been revealed, especially in cardiovascular diseases. Hypertension is one of the most prevalent cardiovascular diseases worldwide, yet whether gut microbiota dysbiosis participates in the development of hypertension remains largely unknown. To investigate this issue, we carried out comprehensive metagenomic and metabolomic analyses in a cohort of 41 healthy controls, 56 subjects with pre-hypertension, 99 individuals with primary hypertension, and performed fecal microbiota transplantation from patients to germ-free mice."
OUTPUT_FILE = "output.txt"
AI_WAIT_TIME = 5
MAX_TOKENS = 2500


def convert_file_to_json(txt_file_path: str) -> str:
    assert ".csv" not in txt_file_path, "Data file should be Tab-separated!"
    try:
        df = pd.read_csv(txt_file_path, sep="\t")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {txt_file_path}")
        return None
    data_dict = df.to_dict(orient='records')
    json_data = json.dumps(data_dict)
    time.sleep(1)
    return str(json_data)


def query_openai(question: str, data_file: str = '', tmax_tokens=MAX_TOKENS, temperature=0.3):
    assert question != "", "Empty question to the model!"
    if tmax_tokens > 14096:
        print("Model's max number of tokens is 4096! Truncating")
        tmax_tokens = 4096
    api_key = os.environ['OPENAI_DISSERTATION_KEY']
    client = OpenAI(api_key=api_key)
    if data_file != '':
        table = convert_file_to_json(data_file)
    else:
        table = ''
    prompt = f"{question}\n\n{table}"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user", "content": prompt
            }
        ],
        model="gpt-3.5-turbo-0125",
        #model="gpt-4",
        #model="gpt-4-32k",
        max_tokens=tmax_tokens,
        temperature=temperature
    )
    time.sleep(AI_WAIT_TIME)
    print(chat_completion.choices[0].message.content)
    with open(OPENAI_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str(datetime.datetime.now())+'\n')
        f.write(str(chat_completion)+'\n\n')
    return chat_completion.choices[0].message.content


