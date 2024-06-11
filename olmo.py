import hf_olmo
from transformers import pipeline


def query_olmo(question: str, data_file: str = "") -> str:
    assert question != "", "Empty question to the model!"
    olmo_pipe = pipeline("text-generation", model="allenai/OLMo-7B")
    response = olmo_pipe(question)
    print(response)
    return response