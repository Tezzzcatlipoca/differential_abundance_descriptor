import re
import os
import pandas as pd
from open_ai import query_openai
from gemini import query_gemini
import requests
import time
import datetime
import tkinter as tk
from tkinter import simpledialog


JOURNALS_SOURCE = "nature.com"
DATASET_GENERATING_PROMPT = f'Use your browser tool to find in {JOURNALS_SOURCE} %num% recent papers about microbiome and %condition%. From each paper, extract its citation information under "Cite this Article" as well as its DOI (only if available), and using only the information included in the papers (and not in your previous training) create a table containing citation information, DOI and paper URLs (both in plain text format, not clickable links) for each one of the %num% papers, and a flag of whether or not the given paper is related with %condition% and contains data of interest (which we will define as information about bacteria species names, phylogeny, gene names and experimental information). The above table should be in a pipe-delimited format with the following columns: Article_Title, Citation_Information, DOI, URL, data_of_interest. The data_of_interest column will be boolean. Each row should refer to an article. Do not include a preamble or introductory paragraph before the table. Only return the tab-separated table.'
TABLES_FIRST_COLUMN = "Article_Title"
WORKING_PATH = "C:\\Users\\Tezzz\\Documents\\Estudios\\Z -MSc Data Science\\999 - DISSERTATION\\LLM_generators2"
URLS_COLUMN = "URL"
INSPECTION_PROMPT = "You are an expert microbiologist. Use your browser tool to read the document available under {url} and using only the information available in the paper (or in its Additional or Supplementary Data), and not in your previous training, create a table about the most outstanding bacteria species that are mentioned in the paper. The table should also contain any information provided about the phylogeny, gene names (and whether they are overexpressed or under-expressed), gene functions (using GO), biochemical pathways and health status. The table should contain the following columns: species_name, phylogeny, gene_name, expression_status, gene_function, biochemical_pathway, health_status, disease_name. If any of the referred pieces of information are not available in the paper or its supplementary data, mark the observation as NA."
SUMMARIZING_PROMPT = ""


def ask_question(this_question: str, data_file: str = "", model='openai') -> bool:
    assert model.lower() in ['gemini', 'openai', 'olmo'], "Available evaluator options are gemini, openai, olmo!"
    if model.lower() == 'gemini':
        response = query_gemini(this_question, data_file)
    elif model.lower() == 'openai':
        response = query_openai(this_question, data_file)
    elif model.lower() == 'olmo':
        #response = query_olmo(this_question, data_file)
        print("OLMo coming soon")
        assert False, f"Language model {model} not available."
    else:
        assert False, f"Language model {model} not available."
    return response


def extract_table(this_response: str) -> pd.DataFrame():
    assert TABLES_FIRST_COLUMN.lower() in this_response.lower(), "Required column is absent from model's response!"
    table_start = this_response.find(TABLES_FIRST_COLUMN)
    table_as_str = this_response[table_start:]
    temp_file = os.path.join(WORKING_PATH, 'temp_list.txt')
    with open(temp_file, 'w', encoding='utf-8') as tf:
        tf.write(table_as_str)
    df = pd.read_csv(temp_file, sep='|', encoding='utf-8')
    return df


def url_checker(docs_list: pd.DataFrame) -> pd.DataFrame:
    assert URLS_COLUMN in docs_list.columns, "No URL column in the model's response!"
    tests_list = []
    for each_url in docs_list[URLS_COLUMN]:
        response = requests.get(each_url)
        time.sleep(4)
        if response.status_code == 200:
            tests_list.append(True)
        else:
            tests_list.append(False)
    docs_list['URL_Exists'] = tests_list
    return docs_list


def ask_parameters() -> dict:
    root = tk.Tk()
    root.withdraw()
    condition = simpledialog.askstring("Input Condition", "Enter the health condition to search for:")
    paper_count = simpledialog.askinteger("Input", "Enter the number of papers to review:")
    return {'%condition%': [condition], '%num%': [paper_count]}


def update_prompt(parameters: dict, this_prompt: str) -> str:
    for each_key in parameters.keys():
        this_value = parameters[each_key][0]
        this_prompt = this_prompt.replace(each_key, str(this_value))
    return this_prompt

def log_response(model_output):
    with open(os.path.join(WORKING_PATH, "response_log.txt"), 'a') as log:
        log.write(f"{datetime.date.today()}\n")
        log.write(f"{str(model_output)}\n\n")
    print("Log saved...")

def inspect_paper(acceptable_papers:pd.DataFrame) -> list:


def generate_dataset_list(model="openai"):
    # Find relevant literature
    user_parameters = ask_parameters()
    updated_prompt = update_prompt(user_parameters, DATASET_GENERATING_PROMPT)
    model_response = ask_question(updated_prompt, data_file="", model=model)
    #log_response(model_response)
    docs_list = extract_table(model_response)
    # Keep relevant sources
    reviewed_docs = url_checker(docs_list)
    clean_docs = reviewed_docs[reviewed_docs['URL_Exists'] == True]
    clean_docs = clean_docs[clean_docs['data_of_interest'] == True]
    # Inspect each relevant source
    # Summarize and draft report
