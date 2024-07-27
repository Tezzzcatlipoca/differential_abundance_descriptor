import pandas as pd
from report_gen_pipeline import *
import numpy as np
from CONSTANTS import *


def get_dummy_parameters():
    return {'%condition%': 'hypertension', '%num%': 3, '%inoculum%': 'https://link.springer.com/article/10.1186/s40168-016-0222-x', '%style_guide%': 'https://ojs.bonviewpress.com/index.php/MEDIN/about/submissions'}


def get_dummy_articles():
    return [['Salivary microbiome and hypertension in the Qatari population',
     'https://translational-medicine.biomedcentral.com/articles/10.1186/s12967-023-04247-8']]


def count_relevant_articles(paper_elements: dict) -> pd.DataFrame:
    # Returns a table with the number of valid articles per
    # scientific journal and condition
    domain_pattern = r'http[s]?://([^/]+)'
    domains = []
    for each_element in paper_elements['%docs_list%']:
        match = re.search(domain_pattern, each_element[URL_INDEX])
        domains.append(match.group(1))
    df = pd.DataFrame({'domain': domains})
    df['count'] = 1
    pivoted = df.groupby('domain').count()
    pivoted.reset_index(inplace=True)
    pivoted['condition'] = paper_elements['%condition%']
    return pivoted


def evaluate_article_relevance(paper_scores: list) -> pd.DataFrame:
    # Returns a table with all journal articles scored by
    # the evaluation criteria, until n valid articles were found
    # (or all original options exhausted)
    def _flatten(xss):
        return [x for xs in xss for x in xs]

    def _score_it(evaluation_text):
        return "Yes" in evaluation_text

    elements_table = []
    for each_score in paper_scores:
        score_elements = each_score.split("\n")
        elements_table.append(score_elements)

    all_criteria = pd.DataFrame()
    for each_criterion in EVALUATION_CRITERIA:
        relevant_evaluations = [x for x in _flatten(elements_table) if each_criterion[1].lower() in x.lower()]
        relevant_scores = [_score_it(x) for x in relevant_evaluations]
        positives = int(np.sum(relevant_scores))
        this_criterion = pd.DataFrame({'criterion': [each_criterion[0]], 'positives': [positives], 'total': [len(relevant_evaluations)]})
        all_criteria = pd.concat([all_criteria, this_criterion])
    return all_criteria


def get_column(columns_list: list, index:int):
    try:
        this_column = columns_list[index]
    except IndexError:
        this_column = ""
    return this_column


def get_bacteria(table_string: str):
    lines = table_string.split("\n")
    bacteria_list = []
    for idx, each_line in enumerate(lines):
        columns = each_line.split("|")
        this_column = get_column(columns, 0)
        if this_column == "":
            this_column = get_column(columns, 1)
        if (idx > 0) and (re.search("[a-z]", this_column.lower()) is not None):
            bacteria_list.append(this_column.strip())
    return bacteria_list


def extract_bacteria_lists_from_text_tables(summaries_list: list):
    # This function extracts the individual bacterial names
    # from LLM-generated text tables
    all_bacteria_lists = []
    for each_summary in summaries_list:
        all_bacteria_lists.append(get_bacteria(each_summary))
    return all_bacteria_lists


def evaluate_paper_false_positives(paper_elements: dict) -> pd.DataFrame:
    all_bacteria_lists = extract_bacteria_lists_from_text_tables(paper_elements['%document_summaries%'])
    all_sources = paper_elements['%acceptable_docs%']
    results_table = pd.DataFrame()
    for x, each_source in enumerate(all_sources):
        each_url = each_source[1]
        page_text = get_page_text(each_url).lower()
        each_individual_list = all_bacteria_lists[x]
        for each_bacteria in each_individual_list:
            is_present = each_bacteria.lower() in page_text
            this_bacteria = pd.DataFrame({'source': [each_url], 'extracted_bacteria': [each_bacteria], 'is_present': [is_present]})
            results_table = pd.concat([results_table, this_bacteria])
    return results_table


def are_consolidated_from_individual(paper_elements: dict) -> pd.DataFrame:
    def _flatten(xss):
        return [x for xs in xss for x in xs]
    consolidated_table = _flatten(extract_bacteria_lists_from_text_tables([paper_elements['%consolidated_table%']]))
    all_bacteria_lists = _flatten(extract_bacteria_lists_from_text_tables(paper_elements['%document_summaries%']))
    is_present = []
    all_bacteria = []
    for each_bacteria in consolidated_table:
        all_bacteria.append(each_bacteria)
        if each_bacteria in all_bacteria_lists:
            is_present.append(True)
        else:
            is_present.append(False)
    output = pd.DataFrame({'each_consolidated': all_bacteria, 'present_in_individual_table': is_present})
    return output


def were_all_individual_consolidated(paper_elements: dict) -> pd.DataFrame:
    def _flatten(xss):
        return [x for xs in xss for x in xs]
    consolidated_table = _flatten(extract_bacteria_lists_from_text_tables([paper_elements['%consolidated_table%']]))
    all_bacteria_lists = _flatten(extract_bacteria_lists_from_text_tables(paper_elements['%document_summaries%']))
    is_present = []
    all_bacteria = []
    for each_original in all_bacteria_lists:
        all_bacteria.append(each_original)
        if each_original in consolidated_table:
            is_present.append(True)
        else:
            is_present.append(False)
    output = pd.DataFrame({'each_original': all_bacteria, 'present_in_consolidated_table': is_present})
    return output


def evaluate_report_formal_elements(final_report_path) -> str:
    evaluation = ask_question(REPORT_EVALUATION_PROMPT, final_report_path)
    time.sleep(10)
    return evaluation


def evaluate_bibliography(final_report_path):
    # Ask the LLM if the bibliography is appropriate
    evaluation = ask_question(BIBLIOGRAPHY_EVALUATION_PROMPT, final_report_path)
    time.sleep(10)
    return evaluation


def evaluate_process(paper_elements: dict):
    relevant_articles = count_relevant_articles(paper_elements)
    relevant_articles.to_csv(os.path.join(WORKING_PATH, EVAL1_PATH), sep="\t", index=False)
    #EVAL2_PATH saved within 'find_n_acceptable' function
    table_bacteria_vs_paper = evaluate_paper_false_positives(paper_elements)
    table_bacteria_vs_paper.to_csv(os.path.join(WORKING_PATH, EVAL3_PATH), sep="\t", index=False)
    consolidated_vs_individual = are_consolidated_from_individual(paper_elements)
    consolidated_vs_individual.to_csv(os.path.join(WORKING_PATH, EVAL4_PATH), sep="\t", index=False)
    individual_vs_consolidated = were_all_individual_consolidated(paper_elements)
    individual_vs_consolidated.to_csv(os.path.join(WORKING_PATH, EVAL5_PATH), sep="\t", index=False)


def evaluate_final_report(report_path: str, report_eval_path: str):
    report_evaluation = evaluate_report_formal_elements(report_path)
    save_results(report_eval_path, report_evaluation)
    # Bibliography review
    bibliography_eval = evaluate_bibliography(report_path)
    save_results(report_eval_path.replace(".txt", "_bibliography.txt"), bibliography_eval)
