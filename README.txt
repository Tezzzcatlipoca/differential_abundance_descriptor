================================================================================
README.txt
================================================================================

Project Name: Differential Abundance Descriptor

================================================================================
Overview:
================================================================================

This repository contains code for generating a differential abundance metanalysis
report. The descriptor helps in finding publicly available data that is relevant,
and then leverages large language models (LLMs) to extract and summarise data, 
and to draft a summary of gathered data.

The code includes an evaluation script that reviews the quality of outputs at 
each step of the process and after report generation, and produces a set of 
evaluation outputs. Evaluation can be disabled by modifying the 'EVALUATING'
constant to 'False' in the CONSTANTS.py file.

================================================================================
Contents:
================================================================================

1. Introduction
2. Installation
3. Usage
4. Examples

================================================================================
1. Introduction
================================================================================

The Differential Abundance Descriptor is a proof of concept designed to analyze 
the possibility of using Large Language Models to generate metanalysis reports
of articles containing differential abundance data for given human health conditions.

Its aim is to explore the state of the art in automated biological data analysis and 
scientific report generation. It is part of a wider study for a dissertation within
the University of Edinburgh's School of Informatics and received little guidance in
microbiology-related topics other than the most significant.

This repository includes scripts and documentation necessary to generate the
a metanalysis report and a set of output and throughput evaluation reports.

The Python script requires access to two commercial LLM engines (Google Gemini and 
Chat GPT), along with valid API tokens for each.

================================================================================
2. Installation
================================================================================

To use the Differential Abundance Descriptor, follow these steps:

- Clone this repository to your local machine:

  git clone https://github.com/Tezzzcatlipoca/differential_abundance_descriptor.git

- Install the required dependencies. Details on dependencies are provided in the
`requirements.txt` file:

  pip install -r requirements.txt

- Store the Google Gemini API key in the computer's 'GOOGLE_API_KEY' environment
  variable.

- Store the ChatGPT API key in the computer's 'OPENAI_KEY' environment variable.

================================================================================
3. Usage
================================================================================

To use the Differential Abundance Descriptor:

- Execute the main script (report_gen_pipeline.py). No command-line parameters 
  expected or accepted. 
- User will be prompted for parameters upon initialisation:
	- Name of the health condition
	- Number of journal article papers to download
	- URL to 'Inoculum' paper
	- URL to style guide (describing the expected style and formal requirements
	  of the final report).
- Follow the prompts or configure settings as per the documentation.

================================================================================
4. How the script works
================================================================================

The script uses a web-scraping function to identify scientific journal articles
relevant to the provided 'health condition' parameter, and then uses LLMs to 
further refine the list. A final list should contain only articles containing the
following elements in data: 

  bacterial species name, phylogeny, gene name, expression status, gene function, 
  biochemical pathway, health condition.

The script then extracts relevant bacterial information from each article and
then consolidates all data into a single table that serves as basis for a
set of two final reports.

The first report is generated using a single LLM prompt, while the second is 
generated using six separate LLM prompts and then stitched together.

================================================================================
5. Examples
================================================================================

Sample output and throughput files are provided in the 'docs\' directory.
Throughput data is available in the form of Python pickle files under the following 
name: 'study_data.pkl'

These can be open to reproduce a run from any point onward. To unpickle a file use
the following Python commands:

  import pickle
  with open("subfolder/study_data.pkl", "rb") as file:
     paper_elements = pickle.load(file)

