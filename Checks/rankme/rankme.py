from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
import numpy as np
import re

def preprocess_text(text):
    """
    Splits the text into meaningful segments based on semicolons and newlines.
    """
    return [segment.strip() for segment in re.split(r'[;\n]', text) if segment.strip()]

def filter_tokens(tokens):
    """
    Filters out non-alphanumeric tokens and those with a length <= 1.
    """
    return [token for token in tokens if token.isalnum() and len(token) > 1]

def compute_entropy(token_counts):
    """
    Computes the entropy of a text based on token counts.
    """
    total_tokens = sum(token_counts.values())
    if total_tokens == 0:
        raise ValueError("Token counts cannot be empty.")
    probabilities = [count / total_tokens for count in token_counts.values()]
    return -sum(p * np.log(p) for p in probabilities if p > 0)

def compute_text_entropy(texts):
    """
    Computes the average entropy of the texts.
    """
    entropies = []
    for text in texts:
        tokens = filter_tokens(text.split())
        token_counts = Counter(tokens)
        if not token_counts:
            continue
        entropy = compute_entropy(token_counts)
        entropies.append(entropy)
    if not entropies:
        raise ValueError("All texts are empty or contain no valid tokens.")
    return np.mean(entropies)

def compute_svd_complexity(texts):
    """
    Computes the complexity of the texts using SVD.
    """
    if not texts or all(len(t.strip()) == 0 for t in texts):
        raise ValueError("Input texts are empty or invalid.")
    vectorizer = CountVectorizer(stop_words=None)
    X = vectorizer.fit_transform(texts)
    if X.shape[0] == 0 or X.shape[1] == 0:
        raise ValueError("Input matrix for SVD is empty.")
    svd = TruncatedSVD(n_components=1)
    svd.fit(X)
    return svd.singular_values_[0]

def compute_rankme_score(texts):
    """
    Computes the RankMe score based on entropy and complexity.    
    """
    avg_entropy = compute_text_entropy(texts)
    complexity = compute_svd_complexity(texts)
    return np.exp(avg_entropy) * complexity

if __name__ == "__main__":
    generated_texts = [
        "#include <iostream>\nint main() { std::cout << \"Hello, World!\"; return 0; }"
    ]

    split_texts = preprocess_text(generated_texts[0]) 
    print(f"Preprocessed Text: {split_texts}")
    try:
        rankme_score = compute_rankme_score(split_texts)
        print(f"RankMe Score: {rankme_score}")
    except ValueError as e:
        print(f"Error: {e}")
