import re
import os
import pandas as pd
from open_ai import query_openai
from gemini import query_gemini
from article_crawler import *
from evaluate_run_pipeline import *
import requests
import time
import datetime
import tkinter as tk
from tkinter import simpledialog
from CONSTANTS import *
import shutil


def ask_question(this_question: str, data_file: str = "", model='openai', tmax_tokens:int=GENERAL_MAX_TOKENS, model_version: str="") -> str:
    assert model.lower() in ['gemini', 'openai', 'olmo'], "Available evaluator options are gemini, openai, olmo!"
    if model.lower() == 'gemini':
        response = query_gemini(this_question, data_file, tmax_tokens=tmax_tokens, model_version=model_version)
    elif model.lower() == 'openai':
        response = query_openai(this_question, data_file, tmax_tokens=tmax_tokens, model_version=model_version)
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
    style_guide = simpledialog.askstring("Style guide source", "Enter a URL to the Style Guide:")
    return {'%condition%': condition, '%num%': paper_count, '%inoculum%': inoculum_paper, '%style_guide%': style_guide}


def extract_inoculum_details(url: str, model=MODEL) -> list:
    new_prompt = INOCULUM_INSPECTION_PROMPT + url
    title = ask_question(new_prompt, model=model)
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


def inspect_paper_elements(this_URL: str, condition: str) -> str:
    new_prompt = INSPECTION_PROMPT.replace('%condition%', condition)
    new_prompt = new_prompt.replace('%URL%', this_URL)
    extracted_info = ask_question(new_prompt, model=MODEL)
    return extracted_info


def extract_text_doi(text: str) -> str:
    doi_pattern = r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b'
    matches = re.findall(doi_pattern, text, re.IGNORECASE)
    if len(matches) == 0:
        output = 'NA'
    else:
        output = matches[0]
    return output


def extract_page_doi(this_URL: str) -> str:
    new_prompt = DOI_PROMPT + " " + this_URL
    findings = ask_question(new_prompt, model=MODEL)
    output = extract_text_doi(findings)
    return output


def save_results(full_path: str, message_to_save:str):
    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(str(datetime.datetime.now())+'\n')
        f.write(str(message_to_save)+'\n\n')


def find_n_acceptable(all_elements: dict) -> list:
    # For each document, this function evaluates the number of positive
    # findings from the list of necessary requirements and adds to the final
    # list any document that has enough findings.
    all_docs = all_elements['%docs_list%']
    condition = all_elements['%condition%']
    n = all_elements['%num%']
    acceptable = []
    evaluations = []
    for each_paper in all_docs:
        print(f"Evaluating {each_paper[0]}...")
        elements = inspect_paper_elements(each_paper[1], condition)
        evaluations.append(elements)
        if elements.count('Yes') >= 5:
            doi = extract_page_doi(each_paper[1])
            each_paper.append(doi)
            acceptable.append(each_paper)
        if acceptable.__len__() == n:
            break
    if acceptable.__len__() < n:
        print(f"Not enough acceptable papers found for {condition}! Only {acceptable.__len__()} found.")
    if EVALUATING:
        scores_table = evaluate_article_relevance(evaluations)
        scores_table.to_csv(EVAL2_PATH, sep="\t", index=False)
    return acceptable


def summarise_document(this_URL: str, model="openai") -> str:
    new_prompt = SUMMARIZING_PROMPT + " " + this_URL
    summary = ask_question(new_prompt, model=model)
    return summary


def append_dois(text_table: str, doi: str):
    def _padd_this(doi: str, first_line: str):
        any_spaces = first_line.count(' ') > 0
        doi_length = len(doi)
        return " "*((doi_length-len('|doi'))*any_spaces)

    def _aesthetic_line(this_line: str) -> bool:
        if len(this_line) == 0:
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


def extract_document_summaries(all_docs: list, model="openai"):
    extracts = []
    for each_paper in all_docs:
        print(f"Summarising {each_paper[0]}...")
        summary = summarise_document(each_paper[1], model)
        summary = append_dois(summary, each_paper[2])
        extracts.append(summary)
    return extracts


def consolidate_tables(document_summaries: list) -> str:
    new_prompt = CONSOLIDATING_PROMPT + "\n".join(document_summaries)
    consolidation = ask_question(new_prompt)
    return consolidation


def draft_article(consolidated_table:str, condition:str, papers:list, model="openai", tmax_tokens=7500) -> str:
    new_prompt = DRAFTING_PROMPT.replace('%table%', consolidated_table) # table, condition, papers
    new_prompt = new_prompt.replace('%condition%', condition)
    new_prompt = new_prompt.replace('%papers%', "\t".join([x[0] + " - " + x[1] + " : " + x[2] for x in papers]))
    article = ask_question(new_prompt, tmax_tokens=tmax_tokens, model=model, model_version="gpt-4")
    return article


def summarize_publication_requirements(magazine_url: str):
    new_prompt = FORMATTING_SUMMARY_PROMPT + magazine_url
    requirements = ask_question(new_prompt)
    return requirements


def draft_abstract(consolidated_table: str, condition: str, inoculum_summary: str) -> str:
    new_prompt = ABSTRACT_DRAFTING_PROMPT.replace('%table%', consolidated_table)
    new_prompt = new_prompt.replace('%condition%', condition)
    new_prompt = new_prompt + inoculum_summary
    abstract = ask_question(new_prompt)
    return abstract


def draft_intro(abstract_summary: str, style_guide: str) -> str:
    new_prompt = INTRO_DRAFTING_PROMPT.replace('%abstract_summary%', abstract_summary)
    new_prompt = new_prompt.replace('%style_guide%', style_guide)
    intro = ask_question(new_prompt)
    return intro


def draft_this(my_prompt: str, my_kwargs: dict, new_element_name: str, attached_file="", tokens=GENERAL_MAX_TOKENS, model='openai') -> dict:
    keywords = re.findall(r'%\w+%', my_prompt)
    new_prompt = my_prompt
    for each_keyword in keywords:
        new_prompt = new_prompt.replace(each_keyword, my_kwargs[each_keyword])
    new_element = ask_question(new_prompt, tmax_tokens=tokens, model=model, data_file=attached_file)
    my_kwargs[new_element_name] = new_element
    return my_kwargs


def stitch(my_kwargs: dict, elements: list) -> str:
    full_text = ""
    for each_element in elements:
        full_text = full_text + my_kwargs[each_element]
    return full_text


def initialize_directory():
    if not os.path.exists(WORKING_PATH):
        os.makedirs(WORKING_PATH)
    if not os.path.exists(LOGS_PATH):
        os.makedirs(LOGS_PATH)


def get_study_path(paper_elements: dict) -> str:
    condition = paper_elements['%condition%']
    assert condition != "", "Provided health condition is empty!"
    condition = condition.replace(' ', '_')
    condition = re.sub('[^A-Za-z0-9\_]+', '', condition)
    condition = condition.lower()
    return condition


def generate_report(model="openai"):
    # Find relevant literature
    paper_elements = ask_parameters()
    initialize_directory()
    paper_elements['%inoculum_details%'] = extract_inoculum_details(paper_elements['%inoculum%'], model='openai')
    paper_elements['%docs_list%'] = get_mixed_links(paper_elements['%condition%'])

    paper_elements['%acceptable_docs%'] = find_n_acceptable(paper_elements)
    paper_elements['%acceptable_docs%'].append(paper_elements['%inoculum_details%'])
    paper_elements['%document_summaries%'] = extract_document_summaries(paper_elements['%acceptable_docs%'], "openai")
    paper_elements['%consolidated_table%'] = consolidate_tables(paper_elements['%document_summaries%'])

    # Summarize and draft report
    paper_elements['%one_shot_article%'] = draft_article(paper_elements['%consolidated_table%'], paper_elements['%condition%'][0], paper_elements['%acceptable_docs%'], 'openai')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%inoculum_details%'][URL_INDEX], paper_elements, '%inoculum_summary%', model='openai')
    paper_elements = draft_this(ABSTRACT_DRAFTING_PROMPT, paper_elements, '%abstract%', model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%abstract%'], paper_elements, '%abstract_summary%', model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%style_guide%'], paper_elements, '%style_summary%', model='gemini')
    paper_elements = draft_this(INTRO_DRAFTING_PROMPT, paper_elements, '%introduction%', model='gemini')
    paper_elements = draft_this(REVIEW_DRAFTING_PROMPT, paper_elements, '%review%', tokens=7000, model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%review%'], paper_elements, '%review_summary%', tokens=7000, model='gemini')
    paper_elements = draft_this(DISCUSSION_DRAFTING_PROMPT, paper_elements, '%discussion%', tokens=7000, model='gemini')
    paper_elements = draft_this(CONCLUSIONS_DRAFTING_PROMPT, paper_elements, '%conclusions%', model='gemini')
    paper_elements = draft_this(ELABORATE_PROMPT + paper_elements['%review_summary%'], paper_elements, '%further_review%', tokens=7000, model='gemini')
    paper_elements['%stitched_text%'] = stitch(paper_elements, ['%abstract%', '%introduction%', '%review%', '%discussion%', '%conclusions%', '%further_review%'])

    with open(os.path.join(WORKING_PATH, PROVISIONAL_REPORT_NAME), 'w') as report1:
        report1.write(paper_elements['%stitched_text%'])

    paper_elements = draft_this(FINETUNING_PROMPT, paper_elements, '%final_stitched%',
                                attached_file=os.path.join(WORKING_PATH, PROVISIONAL_REPORT_NAME), tokens=7000,
                                model='gemini')

    with open(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME2), 'w') as report2:
        report2.write(paper_elements['%final_stitched%'])

    with open(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME1), 'w') as report3:
        report3.write(paper_elements['%one_shot_article%'])

    if EVALUATING:
        evaluate_process(paper_elements)
        evaluate_final_report(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME1), FULL_ART_EVAL1)
        evaluate_final_report(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME2), FULL_ART_EVAL2)

    # Copy all outputs to a study-specific folder
    study_path = get_study_path(paper_elements)
    shutil.copytree(WORKING_PATH, study_path)


if __name__ == "__main__":
    generate_report()
