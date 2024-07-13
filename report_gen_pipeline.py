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


JOURNALS_SOURCE = "nature.com"
DATASET_GENERATING_PROMPT = f'Use your browser tool to find in {JOURNALS_SOURCE} %num% recent papers about microbiome and %condition%. From each paper, extract its citation information under "Cite this Article" as well as its DOI (only if available), and using only the information included in the papers (and not in your previous training) create a table containing citation information, DOI and paper URLs (both in plain text format, not clickable links) for each one of the %num% papers, and a flag of whether or not the given paper is related with %condition% and contains data of interest (which we will define as information about bacteria species names, phylogeny, gene names and experimental information). The above table should be in a pipe-delimited format with the following columns: Article_Title, Citation_Information, DOI, URL, data_of_interest. The data_of_interest column will be boolean. Each row should refer to an article. Do not include a preamble or introductory paragraph before the table. Only return the tab-separated table.'
DOCUMENT_INSPECTION_PROMPT = f''
TABLES_FIRST_COLUMN = "Article_Title"
WORKING_PATH = "C:\\Users\\Tezzz\\Documents\\Estudios\\Z -MSc Data Science\\999 - DISSERTATION\\LLM_generators2"
URLS_COLUMN = "URL"
INOCULUM_INSPECTION_PROMPT = "Provide an APA citation of the paper under the following URL: "
INSPECTION_PROMPT = "From the below URL, extract the following information: \n 1. If it contains Supplementary Information (Yes/No) \n 2. If it contains information on species names (Yes/No) \n 3. If it contains phylogeny (Yes/No) \n 4. If it contains gene names (Yes/No) \n 5. If it contains experimental information on %condition% and control groups (Yes/No) \n These elements can be extracted from the text of the paper or from any Supplementary Data provided with the paper. \n URL: %URL%"
DOI_PROMPT = "From the below URL, extract the DOI. If no DOI is found in the page, return NA. \n Use the following format for your output: \n 10.1038/s41598-018-27682-w \n \n URL: "
SUMMARIZING_PROMPT = "Create a table about the most outstanding bacteria species that are mentioned in the paper. The table should also contain any information provided about the phylogeny, gene names (and whether they are overexpressed or under-expressed), their gene functions (using GO), biochemical pathways and health status. The table should contain the following columns: species_name, phylogeny, gene_name, expression_status, gene_function, biochemical_pathway, health_status, disease_name. If any of the referred pieces of information are not available in the paper or its supplementary data, mark the observation as NA. The table should follow this format example: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension \n\n URL: "
CONSOLIDATING_PROMPT = "Below are %num% table summaries from different microbiology papers about %condition%. You are an expert microbiologist and your task is to consolidate the results from the below tables into a single one, making sure to capture the most important elements. Follow this sample format: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name|DOI\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension|10.1234/a123-456 \n\n Table summaries: "
DRAFTING_PROMPT = "You are an expert microbiologist. Take the below table as the basis to draft an academic paper about the microbiome of %condition% with all of its formal elements. Table \n %table% \n\n The table summarizes the findings from the below list of papers about %condition%. Make sure to cite them in the report. \n List of papers: \n %papers%"
FORMATTING_SUMMARY_PROMPT = "Review the requirements for publishing a paper contained in the below URL and create a concise summary of them. \n URL: "
FINETUNING_PROMPT = ""
ABSTRACT_DRAFTING_PROMPT = "You are an expert microbiologist. Compare the data in the below table (about the microbiome of %condition%) against the provided research paper summary and draft the abstract of a research paper review. \n Table \n %consolidated_table% \n The above table summarizes the findings from a list of related research papers. \n Summary of research paper: \n %inoculum_summary%"
INTRO_DRAFTING_PROMPT = "You are an expert microbiologist. Take the below abstract summary and draft an introduction chapter to it. Whenever relevant, provide real bibliographic references along the text. While drafting, stick to the below style guide \n Abstract Summary\n %abstract_summary% \n Style guide \n %style_summary%"
REVIEW_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create a review of a research paper. Take the below abstract summary and data table and draft a review based in both. Draft only the main body of the review and omit the review’s Introduction, Discussion or Conclusions parts, as these will be drafted by someone else. \n Abstract Summary \n %abstract_summary% \n Data Table \n %consolidated_table% \n Style guide \n %style_summary%"
DISCUSSION_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create the ‘Discussion’ section of a research paper review. Take the below summary of the main body of the review and draft the Discussion section based in it. Draft only the Discussion section of the review and omit the review’s Introduction, Main Body or Conclusions parts, as these will be drafted by someone else. \n Summary of Research Paper Review: \n %review_summary%"
CONCLUSIONS_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create the ‘Conclusions’ section of a research paper review. Take the below summary of the main body of the review and draft the Conclusions section based in it. Draft only the Conclusions section of the review and omit the review’s Introduction, Main Body or Discussions parts, as these will be drafted by someone else. \n Summary of Research Paper Review: \n %review_summary%"
SUMMARY_PROMPT = "Provide a very concise summary of the provided text: "
ELABORATE_PROMPT = "Elaborate further on the below review summary: "
EVALUATING = 0

MODEL = "openai"
OUTPUT_REPORT_NAME = "drafted_article.txt"
GENERAL_MAX_TOKENS = 2500
URL_INDEX = 1


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


def save_results(full_path:str, message_to_save:str):
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


def draft_article(consolidated_table:str, condition:str, papers:list, model="openai", tmax_tokens=10000) -> str:
    new_prompt = DRAFTING_PROMPT.replace('%table%', consolidated_table) # table, condition, papers
    new_prompt = new_prompt.replace('%condition%', condition)
    new_prompt = new_prompt.replace('%papers%', "\t".join([x[0] + " - " + x[1] + " : " + x[2] for x in papers]))
    article = ask_question(new_prompt, tmax_tokens=tmax_tokens, model=model)
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


def draft_this(my_prompt: str, my_kwargs: dict, new_element_name: str, tokens=GENERAL_MAX_TOKENS, model='openai') -> dict:
    keywords = re.findall(r'%\w+%', my_prompt)
    new_prompt = my_prompt
    for each_keyword in keywords:
        new_prompt = new_prompt.replace(each_keyword, my_kwargs[each_keyword])
    new_element = ask_question(new_prompt, tmax_tokens=tokens, model=model)
    my_kwargs[new_element_name] = new_element
    return my_kwargs


def stitch(my_kwargs: dict, elements: list) -> str:
    full_text = ""
    for each_element in elements:
        full_text = full_text + my_kwargs[each_element]
    return full_text


def generate_report(model="openai"):
    # Find relevant literature
    paper_elements = ask_parameters()
    paper_elements['%inoculum_details%'] = extract_inoculum_details(paper_elements['%inoculum%'], model='gemini')
    paper_elements['%docs_list%'] = get_mixed_links(paper_elements['%condition%'])

    # Use spaCy instead?
    paper_elements['%acceptable_docs%'] = find_n_acceptable(paper_elements)
    paper_elements['%acceptable_docs%'].append(paper_elements['%inoculum_details%'])
    paper_elements['%document_summaries%'] = extract_document_summaries(paper_elements['%acceptable_docs%'], "openai")
    paper_elements['%consolidated_table%'] = consolidate_tables(paper_elements['%document_summaries%'])

    # Summarize and draft report
    # article = draft_article(consolidated_table, user_parameters['%condition%'][0], acceptable_docs, 'openai')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%inoculum_details%'][URL_INDEX], paper_elements, '%inoculum_summary%', model='gemini')
    paper_elements = draft_this(ABSTRACT_DRAFTING_PROMPT, paper_elements, '%abstract%', model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%abstract%'], paper_elements, '%abstract_summary%', model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%style_guide%'], paper_elements, '%style_summary%', model='gemini')
    paper_elements = draft_this(INTRO_DRAFTING_PROMPT, paper_elements, '%introduction%', model='gemini')
    paper_elements = draft_this(REVIEW_DRAFTING_PROMPT, paper_elements, '%review%', tokens=7000, model='gemini')
    paper_elements = draft_this(SUMMARY_PROMPT + paper_elements['%review%'], paper_elements, '%review_summary%', tokens=7000, model='gemini')
    paper_elements = draft_this(DISCUSSION_DRAFTING_PROMPT, paper_elements, '%discussion%', tokens=7000, model='gemini')
    paper_elements = draft_this(CONCLUSIONS_DRAFTING_PROMPT, paper_elements, '%conclusions%', model='gemini')
    paper_elements = draft_this(ELABORATE_PROMPT + paper_elements['%review_summary%'], paper_elements, '%further_review%', tokens=7000, model='gemini')
    full_text = stitch(paper_elements, ['%abstract%', '%introduction%', '%review%', '%discussion%', '%conclusions%', '%further_review%'])

    with open(os.path.join(WORKING_PATH, OUTPUT_REPORT_NAME), 'w') as report:
        report.write(full_text)


if __name__ == "__main__":
    generate_report()
