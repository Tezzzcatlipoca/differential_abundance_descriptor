import re
from openai import OpenAI
import pandas as pd
import os
import time

OPENAI_LOG_FILE = 'C:\\Users\\Tezzz\\Documents\\Estudios\\Z -MSc Data Science\\999 - DISSERTATION\\openai_log.txt'
DATA_FILE = "differential_genera_input.txt"
ABSTRACT = "Recently, the potential role of gut microbiome in metabolic diseases has been revealed, especially in cardiovascular diseases. Hypertension is one of the most prevalent cardiovascular diseases worldwide, yet whether gut microbiota dysbiosis participates in the development of hypertension remains largely unknown. To investigate this issue, we carried out comprehensive metagenomic and metabolomic analyses in a cohort of 41 healthy controls, 56 subjects with pre-hypertension, 99 individuals with primary hypertension, and performed fecal microbiota transplantation from patients to germ-free mice."
OUTPUT_FILE = "output.txt"


def ask_gpt4(question, data_table, api_key):
    # Convert the pandas DataFrame to a string format
    data_string = data_table.to_string()

    # Formulate the prompt by appending the data table to the question
    prompt = f"{question}\n\n{data_string}"

    # Set up the API key
    client = OpenAI(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user", "content": prompt
            }
        ],
        #model="gpt-3.5-turbo-0125",
        model="gpt-4o",
        max_tokens=2500
    )

    # Return the response text
    return chat_completion


def save_output(this_answer):
    def _next_available_filename(file_name:str) -> str:
        before_extension = file_name.replace(".txt", "")
        all_numbers = re.findall("\d+", before_extension)
        count_of_numbers = len(all_numbers)
        if count_of_numbers == 0:
            consecutive = 2
            number_of_digits = 0
        else:
            final_number = all_numbers[count_of_numbers - 1]
            number_of_digits = len(final_number)
            last_digits = before_extension[-number_of_digits:]
            if last_digits == final_number:
                consecutive = int(last_digits) + 1
            else:
                consecutive = 2
                number_of_digits = 0
        new_name = before_extension[0:len(before_extension)-number_of_digits] + str(consecutive)
        return new_name + ".txt"

    file_name = OUTPUT_FILE
    while os.path.isfile(file_name):
        file_name = _next_available_filename(file_name)

    with open(file_name, 'w') as f:
        f.write(str(answer.usage))
        f.write(answer.choices[0].message.content)


# Example usage
if __name__ == "__main__":
    api_key = os.environ['OPENAI_DISSERTATION_KEY']

    # Sample data table
    df = pd.read_csv(DATA_FILE, sep="\t")

    prompt = "You are a microbiologist. Write a scientific report based on the following research objectives, together with the findings of the differential abundance analysis table attached. Provide recent references with real DOI, including authors and titles. \n"
    query = prompt + ABSTRACT
    # Ask GPT-4
    answer = ask_gpt4(query, df, api_key)
    time.sleep(5)
    print(answer)
    save_output(answer)
