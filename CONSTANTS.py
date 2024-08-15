# MAIN
JOURNALS_SOURCE = "nature.com"
TABLES_FIRST_COLUMN = "Article_Title"
LOGS_PATH = "logs/"
WORKING_PATH = "output/"
URLS_COLUMN = "URL"
MODEL = "openai"
OUTPUT_REPORT_NAME1 = "one_shot_article.txt"
OUTPUT_REPORT_NAME2 = "stitched_article.txt"
PROVISIONAL_REPORT_NAME = "provisional_article.txt"
STUDY_OBJECT = "study_data.pkl"
GENERAL_MAX_TOKENS = 2500
EVALUATING = True


# LLM PROMPTS
#DATASET_GENERATING_PROMPT = f'Use your browser tool to find in {JOURNALS_SOURCE} %num% recent papers about microbiome and %condition%. From each paper, extract its citation information under "Cite this Article" as well as its DOI (only if available), and using only the information included in the papers (and not in your previous training) create a table containing citation information, DOI and paper URLs (both in plain text format, not clickable links) for each one of the %num% papers, and a flag of whether or not the given paper is related with %condition% and contains data of interest (which we will define as information about bacteria species names, phylogeny, gene names and experimental information). The above table should be in a pipe-delimited format with the following columns: Article_Title, Citation_Information, DOI, URL, data_of_interest. The data_of_interest column will be boolean. Each row should refer to an article. Do not include a preamble or introductory paragraph before the table. Only return the tab-separated table.'
# Without Phylogeny
DATASET_GENERATING_PROMPT = f'Use your browser tool to find in {JOURNALS_SOURCE} %num% recent papers about microbiome and %condition%. From each paper, extract its citation information under "Cite this Article" as well as its DOI (only if available), and using only the information included in the papers (and not in your previous training) create a table containing citation information, DOI and paper URLs (both in plain text format, not clickable links) for each one of the %num% papers, and a flag of whether or not the given paper is related with %condition% and contains data of interest (which we will define as information about bacteria species names, gene names and experimental information). The above table should be in a pipe-delimited format with the following columns: Article_Title, Citation_Information, DOI, URL, data_of_interest. The data_of_interest column will be boolean. Each row should refer to an article. Do not include a preamble or introductory paragraph before the table. Only return the tab-separated table.'

INOCULUM_INSPECTION_PROMPT = "Provide an APA citation of the paper under the following URL: "
#INSPECTION_PROMPT = "From the below URL, extract the following information: \n 1. If it contains Supplementary Information (Yes/No) \n 2. If it contains information on species names (Yes/No) \n 3. If it contains phylogeny (Yes/No) \n 4. If it contains gene names (Yes/No) \n 5. If it contains experimental information on %condition% and control groups (Yes/No) \n These elements can be extracted from the text of the paper or from any Supplementary Data provided with the paper. \n URL: %URL%"
# Without Pyholgeny
INSPECTION_PROMPT = "From the below URL, extract the following information: \n 1. If it contains Supplementary Information (Yes/No) \n 2. If it contains information on species names (Yes/No) \n 3. If it contains gene names (Yes/No) \n 4. If it contains experimental information on %condition% and control groups (Yes/No) \n These elements can be extracted from the text of the paper or from any Supplementary Data provided with the paper. \n URL: %URL%"
NUMBER_OF_ELEMENTS = 4  # 4 without Phylogeny, 5 otherwise
DOI_PROMPT = "From the below URL, extract the DOI. If no DOI is found in the page, return NA. \n Use the following format for your output: \n 10.1038/s41598-018-27682-w \n \n URL: "
SUMMARIZING_PROMPT = "Create a table about the most outstanding bacteria species that are mentioned in the paper. The table should also contain any information provided about the phylogeny, gene names (and whether they are overexpressed or under-expressed), their gene functions (using GO), biochemical pathways and health status. The table should contain the following columns: species_name, phylogeny, gene_name, expression_status, gene_function, biochemical_pathway, health_status, disease_name. If any of the referred pieces of information are not available in the paper or its supplementary data, mark the observation as NA. The table should follow this format example: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension \n\n URL: "
CONSOLIDATING_PROMPT = "Below are %num% table summaries from different microbiology papers about %condition%. You are an expert microbiologist and your task is to consolidate the results from the below tables into a single one, making sure to capture the most important elements. Follow this sample format: \n species_name|phylogeny|gene_name|expression_status|gene_function|biochemical_pathway|health_status|disease_name|DOI\nBacteroides fragilis|Bacteroidetes|butyryl-CoA CoA-transferase|Overexpressed|GO:0006084|Butyrate biosynthesis|Hypertensive|Hypertension|10.1234/a123-456 \n\n Table summaries: "
DRAFTING_PROMPT = "You are an expert microbiologist. Take the below table as the basis to draft an academic paper about the microbiome of %condition% with all of its formal elements. Table \n %table% \n\n The table summarizes the findings from the below list of papers about %condition%. Make sure to cite them in the report. \n List of papers: \n %papers%"
FORMATTING_SUMMARY_PROMPT = "Review the requirements for publishing a paper contained in the below URL and create a concise summary of them. \n URL: "
FINETUNING_PROMPT = "Re-organize and proof-read the contents of the attached file. Avoid providing any explanations on the changes. Only re-organize and improve the document to resemble a good scientific report. While drafting, stick to the below style guide \n Abstract Summary\n %abstract_summary% \n Style guide \n %style_summary% "
ABSTRACT_DRAFTING_PROMPT = "You are an expert microbiologist. Compare the data in the below table (about the microbiome of %condition%) against the provided research paper summary and draft the abstract of a research paper review. \n Table \n %consolidated_table% \n The above table summarizes the findings from a list of related research papers. \n Summary of research paper: \n %inoculum_summary%"
INTRO_DRAFTING_PROMPT = "You are an expert microbiologist. Take the below abstract summary and draft an introduction chapter to it. Whenever relevant, provide real bibliographic references along the text. \n ABSTRACT \n  %abstract% \n "
REVIEW_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create a review of a research paper. Take the below abstract summary and data table and draft a review based in both. Draft only the main body of the review and omit the review’s Introduction, Discussion or Conclusions parts, as these will be drafted by someone else. \n Abstract Summary \n %abstract_summary% \n Data Table \n %consolidated_table% "
DISCUSSION_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create the ‘Discussion’ section of a research paper review. Take the below summary of the main body of the review and draft the Discussion section based in it. Draft only the Discussion section of the review and omit the review’s Introduction, Main Body or Conclusions parts, as these will be drafted by someone else. \n Summary of Research Paper Review: \n %review_summary%"
CONCLUSIONS_DRAFTING_PROMPT = "You are an expert microbiologist. You were given the task to create the ‘Conclusions’ section of a research paper review. Take the below summary of the main body of the review and draft the Conclusions section based in it. Draft only the Conclusions section of the review and omit the review’s Introduction, Main Body or Discussions parts, as these will be drafted by someone else. \n Summary of Research Paper Review: \n %review_summary%"
SUMMARY_PROMPT = "Provide a very concise summary of the provided text: "
STYLE_SUMMARY_PROMPT = "Create a list of the stylistic requirements mentioned in the below text."
ELABORATE_PROMPT = "Elaborate further on the below review summary: "


# OpenAI API
OPENAI_LOG_FILE = 'openai_log.txt'
DATA_FILE = "differential_genera_input.txt"
ABSTRACT = "Recently, the potential role of gut microbiome in metabolic diseases has been revealed, especially in cardiovascular diseases. Hypertension is one of the most prevalent cardiovascular diseases worldwide, yet whether gut microbiota dysbiosis participates in the development of hypertension remains largely unknown. To investigate this issue, we carried out comprehensive metagenomic and metabolomic analyses in a cohort of 41 healthy controls, 56 subjects with pre-hypertension, 99 individuals with primary hypertension, and performed fecal microbiota transplantation from patients to germ-free mice."
OUTPUT_FILE = "output.txt"
AI_WAIT_TIME = 5
MAX_TOKENS = 2500

# Gemini API
WAIT_TIME = 5
GOOGLE_LOG_FILE = 'google_log.txt'

# Evaluation
URL_INDEX = 1
BIBLIOGRAPHY_EVALUATION_PROMPT = "You are an expert microbiologist. Please evaluate the attached scientific report's bibliography to determine its relevance to the overall topic. Specifically, assess if the sources cited are appropriate and pertinent to the subject matter. Additionally, identify any significant papers or key references that may be missing from the bibliography."
REPORT_EVALUATION_PROMPT = "From the attached scientific report, evaluate its formal elements and enumerate its strengths and its weaknesses."
if NUMBER_OF_ELEMENTS == 4:
    EVALUATION_CRITERIA = [['Supplementary Information', '1.'], ['Species names', '2.'], ['Gene names', '3.'], ['Experimental information', '4.']]
else:
    EVALUATION_CRITERIA = [['Supplementary Information', '1.'], ['Species names', '2.'], ['Phylogeny', '3.'],
                           ['Gene names', '4.'], ['Experimental information', '5.']]
EVAL1_PATH = "evaluation/1_articles_from_query.txt"
EVAL2_PATH = "evaluation/2_article_relevance.txt"
EVAL3_PATH = "evaluation/3_bacteria_relevance.txt"
EVAL4_PATH = "evaluation/4_consolidated_vs_individual.txt"
EVAL5_PATH = "evaluation/5_individual_vs_consolidated.txt"
EVAL6_ONE_SHOT_PATH = "evaluation/6_final_report_one_shot.txt"
EVAL6_STITCHED_PATH = "evaluation/6_final_report_stitched.txt"


### ---------------------------- Paper vs Paper evaluation ----------------------------------
GENERATING_PROMPT = "You are a microbiologist. Write a scientific report based on the following research objectives, together with the findings of the differential abundance analysis table attached. Provide recent references with real DOI, including authors and titles. \n"
SINGLE_EVALUATION_PROMPT = """Below is an academic text and you are an expert microbiologist. Review the article and provide an expert opinion regarding the following: \n 1. General quality of the paper. \n 2. Text coherence. \n 3. Formal elements. \n 4. Originality and usefulness of any findings. \n\n Academic Text: \n"""
PAIR_EVALUATION_PROMPT = """Below are two academic texts. Each one was drafted by a different author. The first author may have had access to more complete data than the second one but both authors had access to some of the same data. Evaluate if the second text is compatible with any findings or conclusions of the first text. Only answer True or False, as in the example below: 
PRIMARY TEXT:
Patients suffering from cancer, heart failure, renal failure, smoking, stroke, peripheral artery disease, and chronic inflammatory disease were all excluded.
----------------
SECONDARY TEXT:
We did not include in the study any patients that smoked.
----------------
Answer:
True
----------------
"""

EXAMPLE1_ORIGINAL = """pHTN and HTN-associated genera in GM
Genes were aligned to the NR database and annotated to taxonomic groups. The relative abundance of gut microbes was calculated by summing the abundance of genes as listed in Additional file 2: Table S3–S4. P values were tested by Wilcoxon rank sum test and corrected
for multiple testing with Benjamin & Hochberg method as others previously did [4, 25]. It is worth mentioning that 44 genera were differentially enriched in control, pHTN, and HTN (P < 0.1, Wilcoxon rank sum test, Fig. 2a and Additional file 2: Table S5). Fifteen of them
were further shown in Fig. 2b. Genera such as Prevotella and Klebsiella were overrepresented in individuals with pHTN or HTN (Fig. 2b). Prevotella, originated from mouth and vagina, was abundant in the microbiome of our study cohort. The pathogenesis of periodontal
diseases and rheumatoid arthritis are thought to be attributed to Prevotella [3, 26]. A wide range of infectious diseases are known to be attributed to Klebsiella [27, 28]. Porphyromonas and Actinomyces, which were also elevated in the HTN group, are morbific oral bacteria
that cause infections and periodontal diseases [29].

By contrast, Faecalibacterium, Oscillibacter, Roseburia, Bifidobacterium, Coprococcus, and Butyrivibrio, which were enriched in healthy controls, declined in pHTN and HTN patients (Fig. 2b). Our observations were consistent with the genera negatively correlated with Prevotella in the network of enterotype 1 (Additional file 4: Figure S2), and these bacteria are known to be essential for healthy status. For example, reduced levels of Faecalibacterium and Roseburia in the intestines are associated with Crohn’s disease and ulcerative colitis [30,
31]. Both bacteria are crucial for butyric acid production [30, 32]. Moreover, Bifidobacterium is an important probiotic necessary to intestinal microbial homeostasis, gut barrier, and lipopolysaccharide (LPS) reduction [33].

The divergence of GM composition in each sample was assessed to explore the correlation of microbial abundance with body mass index (BMI), age, and gender (Additional file 5: Figure S3). Although the gender ratio is discrepant among groups (Additional file 1: Table S1),
we found no remarkable regularity of bacterial abundance based on BMI, age or gender.

To further validate the bacterial alterations in HTN, an independent metagenomic analysis was performed using the sequencing data generated from a previous study of type 2 diabetes [2]. From a total of 174 nondiabetic controls in the study, normotensive controls
with SBP ≤125 mmHg or DBP ≤80 mmHg were enrolled, and HTN were elected with the inclusion criteria of SBP ≥150 mmHg or DBP ≥100 mmHg. The FBG levels between normotensive controls and HTN were similar. Finally, six subjects (HTNs, n = 3; normotensive controls, n = 3) were included in our analysis (Additional file 2: Table S6). As expected, the microbial diversity was decreased in HTN (Additional file 6: Figure S4a), and there were at least 20 genera showing consistent trends with our findings, including decreased Butyrivibrio, Clostridium, Faecalibacterium, Enterococcus, Roseburia, Blautia, Oscillbacter, and elevated Klebsiella, Prevotella, and Desulfovibrio (Additional file 6: Figure S4b, Additional file 2: Table S7).

Collectively, these results supported our hypothesis that bacteria associated with healthy status were reduced in patients with HTN. This phenomenon together with the overgrowth of bacteria such as Prevotella and Klebsiella may play important role in the pathology of HTN."""

EXAMPLE1_GENERATED = """### Research Objectives:
The main research objective of this study was to investigate the potential role of gut microbiota dysbiosis in the development of hypertension, one of the most prevalent cardiovascular diseases worldwide. This was done through comprehensive metagenomic and metabolomic analyses in a cohort of 41 healthy controls, 56 subjects with pre-hypertension, and 99 individuals with primary hypertension. Additionally, fecal microbiota transplantation from patients to germ-free mice was performed to further understand the influence of gut microbiota on hypertension.

### Findings of the Differential Abundance Analysis:
The differential abundance analysis revealed significant differences in the abundance of various genera in the gut microbiota of individuals with different blood pressure statuses. Some key findings include:
1. **Prevotella**: Showed a slight increase in abundance in individuals with pre-hypertension compared to healthy controls.
2. **Faecalibacterium**: Demonstrated a decrease in abundance in both pre-hypertensive and hypertensive individuals compared to healthy controls.
3. **Klebsiella**: Showed a significant increase in abundance in individuals with pre-hypertension and primary hypertension.
4. **Roseburia**: Demonstrated a slight decrease in abundance in hypertensive individuals compared to healthy controls.
5. **Enterobacter**: Displayed a slight increase in abundance in pre-hypertensive individuals compared to hypertensive individuals.
6. **Clostridium**: Showed differences in abundance in both pre-hypertensive and hypertensive individuals compared to healthy controls.
7. **Akkermansia**: Displayed variations in abundance in both pre-hypertensive and hypertensive individuals compared to healthy controls.
8. **Blautia, Lachnoclostridium, Streptococcus, Veillonella**: Showed significant differences in abundance in pre-hypertensive individuals compared to healthy controls.
"""
