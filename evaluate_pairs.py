import re
import os
from open_ai import query_openai
from gemini import query_gemini
#from olmo import query_olmo

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
