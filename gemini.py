import os
import pandas as pd
import json
import google.generativeai as genai
import time
import datetime
from CONSTANTS import *

# Allowed rate: 60 requests per minute (Min Wait time == 1)


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


def query_gemini(question: str, data_file: str = "", tmax_tokens=MAX_TOKENS, model_version: str="gemini-1.5-flash") -> str:
    assert question != "", "Empty question to the model!"
    if model_version == "":
        model_version = "gemini-1.5-flash"
    gm_api_key = os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=gm_api_key)
    model = genai.GenerativeModel(model_version, generation_config=genai.types.GenerationConfig(
        # Only one candidate for now.
        candidate_count=1,
        max_output_tokens=tmax_tokens,
        temperature=1.0))
    if data_file != "":
        table = ingest_file(data_file)
        response = model.generate_content(f"{question}\n\n{table}", stream=False)
    else:
        response = model.generate_content(question, stream=False)
    time.sleep(WAIT_TIME)
    print(response.text)
    with open(os.path.join(LOGS_PATH, GOOGLE_LOG_FILE), 'a', encoding='utf-8') as f:
        f.write(str(datetime.datetime.now())+'\n')
        f.write(str(response)+'\n\n')
    return response.text

#model.count_tokens("What is the meaning of life?")
#model.count_tokens(chat.history)

