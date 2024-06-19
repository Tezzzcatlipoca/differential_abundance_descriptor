import re
import os
import pandas as pd
from open_ai import query_openai
from gemini import query_gemini
from article_crawler import *
import requests
import time
import datetime
import tkinter as tk
from tkinter import simpledialog


JOURNALS_SOURCE = "nature.com"
DATASET_GENERATING_PROMPT = f'Use your browser tool to find in {JOURNALS_SOURCE} %num% recent papers about microbiome and %condition%. From each paper, extract its citation information under "Cite this Article" as well as its DOI (only if available), and using only the information included in the papers (and not in your previous training) create a table containing citation information, DOI and paper URLs (both in plain text format, not clickable links) for each one of the %num% papers, and a flag of whether or not the given paper is related with %condition% and contains data of interest (which we will define as information about bacteria species names, phylogeny, gene names and experimental information). The above table should be in a pipe-delimited format with the following columns: Article_Title, Citation_Information, DOI, URL, data_of_interest. The data_of_interest column will be boolean. Each row should refer to an article. Do not include a preamble or introductory paragraph before the table. Only return the tab-separated table.'
DOCUMENT_INSPECTION_PROMPT = f''
TABLES_FIRST_COLUMN = "Article_Title"
WORKING_PATH = "C:\\Users\\Tezzz\\Documents\\Estudios\\Z -MSc Data Science\\999 - DISSERTATION\\LLM_generators2"
URLS_COLUMN = "URL"
INOCULUM_INSPECTION_PROMPT = "Using your browsing tool, check if the below URL exists, and if so, return the title of the academic paper under the URL. If the URL is not valid or returns no scientific paper, then return 'Not a paper'. Respond following this format: \n User: http://www.non-existent-paper.com/ \n Model: Not a paper \n User: https://www.nature.com/articles/35079176 \n Model: Natural selection and resistance to HIV \n\n --------------------- \n URL:"
INSPECTION_PROMPT = "From the below URL, extract the following information: \n 1. If it contains Supplementary Information (Yes/No) \n 2. If it contains information on species names (Yes/No) \n 3. If it contains phylogeny (Yes/No) \n 4. If it contains gene names (Yes/No) \n 5. If it contains experimental information on %condition% and control groups (Yes/No) \n These elements can be extracted from the text of the paper or from any Supplementary Data provided with the paper. \n URL: %URL%"
DOI_PROMPT = "From the below URL, extract the DOI. If no DOI is found in the page, return NA. \n Use the following format for your output: \n 10.1038/s41598-018-27682-w \n \n URL: "
SUMMARIZING_PROMPT = "You are an expert microbiologist. Use your browser tool to read the document available under de below URL and using only the information available in the paper (or in its Additional or Supplementary Information), and not in your previous training, create a table about the most outstanding bacteria species that are mentioned in the paper. The table should also contain any information provided about the phylogeny, gene names (and whether they are overexpressed or under-expressed), their gene functions (using GO), biochemical pathways and health status. The table should contain the following columns: species_name, phylogeny, gene_name, expression_status, gene_function, biochemical_pathway, health_status, disease_name. If any of the referred pieces of information are not available in the paper or its supplementary data, mark the observation as NA. The table should follow this format example: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension \n\n URL: "
CONSOLIDATING_PROMPT = "Below are %num% table summaries from different microbiology papers about %condition%. You are an expert microbiologist and your task is to consolidate the results from the below tables into a single one, making sure to capture the most important elements. Follow this sample format: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name|DOI\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension|10.1234/a123-456 \n\n Table summaries: "
DRAFTING_PROMPT = "You are an expert microbiologist. Take the below table as the basis to draft an academic paper about the microbiome of %condition% with all of its formal elements. Table \n %table% \n\n The table summarizes the findings from the below list of papers about %condition%. Make sure to cite them in the report. \n List of papers: \n %papers%"
FORMATTING_SUMMARY_PROMPT = "Review the requirements for publishing a paper contained in the below URL and create a concise summary of them. \n URL: "
FINETUNING_PROMPT = "From the "
MODEL = "openai"
OUTPUT_REPORT_NAME = "drafted_article.txt"
GENERAL_MAX_TOKENS = 2500


def ask_question(this_question: str, data_file: str = "", model='openai', tmax_tokens:int=GENERAL_MAX_TOKENS) -> str:
    assert model.lower() in ['gemini', 'openai', 'olmo'], "Available evaluator options are gemini, openai, olmo!"
    if model.lower() == 'gemini':
        response = query_gemini(this_question, data_file, tmax_tokens=tmax_tokens)
    elif model.lower() == 'openai':
        response = query_openai(this_question, data_file, tmax_tokens=tmax_tokens)
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
    inoculum_paper = simpledialog.askstring("Inoculum paper", "Enter the URL to any paper that needs to be ingested:")
    return {'%condition%': [condition], '%num%': [paper_count], '%inoculum%': [inoculum_paper]}


def extract_inoculum_details(url: str) -> list:
    new_prompt = INOCULUM_INSPECTION_PROMPT + url
    title = ask_question(new_prompt, model=MODEL)
    doi = extract_page_doi(url)
    assert 'not a paper' not in title.lower(), "URL to the Inoculum Paper does not return a valid paper!"
    return [title, url, doi]


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


def inspect_paper_elements(this_URL:str, condition:str) -> list:
    new_prompt = INSPECTION_PROMPT.replace('%condition%', condition)
    new_prompt = new_prompt.replace('%URL%', this_URL)
    extracted_info = ask_question(new_prompt, model=MODEL)
    return extracted_info


def extract_text_doi(text:str) -> str:
    doi_pattern = r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b'
    matches = re.findall(doi_pattern, text, re.IGNORECASE)
    if len(matches) == 0:
        output = 'NA'
    else:
        output = matches[0]
    return output


def extract_page_doi(this_URL:str) -> str:
    new_prompt = DOI_PROMPT + " " + this_URL
    findings = ask_question(new_prompt, model=MODEL)
    output = extract_text_doi(findings)
    return output


def find_n_acceptable(all_docs:list, n:int, condition:str) -> list:
    # For each document, this function evaluates the number of positive
    # findings from the list of necessary requirements and adds to the final
    # list any document that has enough findings.
    acceptable = []
    for each_paper in all_docs:
        print(f"Evaluating {each_paper[0]}...")
        elements = inspect_paper_elements(each_paper[1], condition)
        if elements.count('Yes') >= 5:
            doi = extract_page_doi(each_paper[1])
            each_paper.append(doi)
            acceptable.append(each_paper)
        if acceptable.__len__() == n:
            break
    if acceptable.__len__() < n:
        print(f"Not enough acceptable papers found for {condition}! Only {acceptable.__len__()} found.")
    return acceptable


def summarise_document(this_URL:str, model="openai") -> str:
    new_prompt = SUMMARIZING_PROMPT + " " + this_URL
    summary = ask_question(new_prompt, model=model)
    return summary


def append_dois(text_table:str, doi:str):
    def _padd_this(doi:str, first_line:str):
        any_spaces = first_line.count(' ') > 0
        doi_length = len(doi)
        return " "*((doi_length-len('|doi'))*any_spaces)

    def _aesthetic_line(this_line:str) -> bool:
        if len(this_line)==0:
            output = False
        else:
            output = this_line.count('-')/len(this_line) > .5
        return output

    if doi.lower() == 'na':
        doi = 'NA ' # For table aesthetics purposes

    new_table = ""
    lines = text_table.split('\n')
    padding = _padd_this(doi, lines[0])
    count = 0
    # Some tables have outer boundaries, some don't
    if text_table[-1] == '|':
        ending_char = -1
    else:
        ending_char = 10000
    for each_line in lines:
        if count == 0:
            new_line = each_line[0:ending_char] + '|doi' + padding + '|'
        elif _aesthetic_line(each_line):
            new_line = each_line[0:ending_char] + '|---' + padding.replace(' ', '-') + '|'
        else:
            if len(new_line) > 0:
                new_line = each_line[0:ending_char] + '|' + str(doi) + '|'
            else:
                new_line = each_line
        count = count + 1
        new_table = new_table + '\n' + new_line
    return new_table[1:]


def extract_document_summaries(all_docs:list, model="openai"):
    extracts = []
    for each_paper in all_docs:
        print(f"Summarising {each_paper[0]}...")
        summary = summarise_document(each_paper[1], model)
        summary = append_dois(summary, each_paper[2])
        extracts.append(summary)
    return extracts


def consolidate_tables(document_summaries:list) -> str:
    new_prompt = CONSOLIDATING_PROMPT + "\n".join(document_summaries)
    consolidation = ask_question(new_prompt)
    return consolidation


def draft_article(consolidated_table:str, condition:str, papers:list, model="openai") -> str:
    new_prompt = DRAFTING_PROMPT.replace('%table%', consolidated_table) # table, condition, papers
    new_prompt = new_prompt.replace('%condition%', condition)
    new_prompt = new_prompt.replace('%papers%', "\t".join([x[0] + " - " + x[1] + " : " + x[2] for x in papers]))
    article = ask_question(new_prompt, tmax_tokens=10000, model=model)
    return article


def summarize_publication_requirements(magazine_url:str):
    new_prompt = FORMATTING_SUMMARY_PROMPT + magazine_url
    requirements = ask_question(new_prompt)
    return requirements


def generate_report(model="openai"):
    # Find relevant literature
    user_parameters = ask_parameters()
    inoculum_details = extract_inoculum_details(user_parameters['%inoculum%'][0])
    # Verify that the Journal exists!
    docs_list = get_mixed_links(user_parameters['%condition%'][0])
    # Add other media besides Nature, then re-order them randomly

    # Inspect each page, check for elements.
    # This step can be done outside of a paid LLM, to reduce costs when
    # analysing hundreds of papers for suitability, using a spaCy?
    acceptable_docs = find_n_acceptable(docs_list, user_parameters['%num%'][0], user_parameters['%condition%'][0])
    acceptable_docs.append(inoculum_details)
    document_summaries = extract_document_summaries(acceptable_docs, "openai")
    consolidated_table = consolidate_tables(document_summaries)

    # Summarize and draft report
    article = draft_article(consolidated_table, user_parameters['%condition%'][0], acceptable_docs, 'openai')
    with open(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME), 'w') as report:
        report.write(article)


if __name__ == "__main__":
    generate_report()
