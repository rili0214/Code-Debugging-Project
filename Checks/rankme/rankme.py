import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests

def compute_rankme(Z, epsilon=1e-7):
    U, sigma, Vt = np.linalg.svd(Z, full_matrices=False)
    sigma_sum = np.sum(sigma) + epsilon
    p_k = sigma / sigma_sum
    entropy = -np.sum(p_k * np.log(p_k + epsilon))
    rankme = np.exp(entropy)
    return rankme

model_name = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, output_hidden_states=True)

buggy_code = "def quicksort(arr): if len(arr) <= 1: return arr else: pivot = arr[0] return quicksort([x for x in arr[1:] if x <= pivot]) + [pivot] + quicksort([x for x in arr[1:] if x > pivot])"

huggingface_api_token = "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"
headers = {"Authorization": f"Bearer {huggingface_api_token}"}
url = f"https://api-inference.huggingface.co/models/{model_name}"
prompt = f"Debug the following Python code:\n\n{buggy_code}\n\nCorrected code:"

response = requests.post(url, headers=headers, json={"inputs": prompt})
corrected_code = response.json().get('generated_text', '')

print(f"Corrected Code:\n{corrected_code}")

inputs = tokenizer(corrected_code, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

hidden_states = outputs.hidden_states[-1]

sequence_embedding = hidden_states.mean(dim=1).numpy()

rankme_score = compute_rankme(sequence_embedding)
print(f"RankMe Score: {rankme_score}")