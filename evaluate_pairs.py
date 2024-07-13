import re
import os
from open_ai import query_openai
from gemini import query_gemini
#from olmo import query_olmo
from CONSTANTS import *


def _next_available_filename(file_name: str) -> str:
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
    new_name = before_extension[0:len(before_extension) - number_of_digits] + str(consecutive)
    return new_name + ".txt"


def save_output(this_answer, file_name):
    #file_name = OUTPUT_FILE
    #while os.path.isfile(file_name):
    #    file_name = _next_available_filename(file_name)

    with open(file_name, 'w') as f:
        f.write(str(this_answer.usage))
        f.write(this_answer.choices[0].message.content)


def evaluate_text(generated_text:str, evaluator:'openai') -> str:
    assert evaluator.lower() in ['gemini', 'openai', 'olmo'], "Available evaluator options are gemini, openai, olmo!"
    complete_prompt = SINGLE_EVALUATION_PROMPT + generated_text
    if evaluator.lower() == 'gemini':
        response = query_gemini(complete_prompt)
    elif evaluator.lower() == 'openai':
        response = query_openai(complete_prompt)
    elif evaluator.lower() == 'olmo':
        #response = query_olmo(complete_prompt)
        print("OLMo coming soon")
    else:
        assert False, f"Evaluation model {evaluator} not available."
    return response


def evaluate_text_pair(original_text: str, generated_text: str, evaluator='gemini') -> bool:
    assert evaluator.lower() in ['gemini', 'openai', 'olmo'], "Available evaluator options are gemini, openai, olmo!"
    complete_prompt = f"""{PAIR_EVALUATION_PROMPT}
    PRIMARY TEXT: 
    {original_text}
    ----------------
    SECONDARY TEXT:
    {generated_text}
    ----------------
    Answer:"""

    if evaluator.lower() == 'gemini':
        response = query_gemini(complete_prompt)
    elif evaluator.lower() == 'openai':
        response = query_openai(complete_prompt)
    elif evaluator.lower() == 'olmo':
        #response = query_olmo(complete_prompt)
        print("OLMo coming soon")
    else:
        assert False, f"Evaluation model {evaluator} not available."
    return response


if __name__ == "__main__":
    evaluation = evaluate_text_pair(EXAMPLE1_ORIGINAL, EXAMPLE1_GENERATED)
    print("Automated Coherence Evaluation")
    print(f"Result: {evaluation}")
    print("Original text:")
    print(EXAMPLE1_ORIGINAL)
    print("LLM-Generated text:")
    print(EXAMPLE1_GENERATED)
    #save_output(answer)
