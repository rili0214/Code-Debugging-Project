import re
from typing import List, Tuple

def extract_and_select_best_code_block(text):
    """
    Extract and select the most likely correct code block from the text.
    """
    if text == "" or text == " ": return ""

    # Keywords for prioritizing blocks
    keywords = ["correct", "updated", "efficient", "enhanced", "optimized", "revised"]

    # Extract code blocks surrounded by triple backticks (with or without language specifier)
    fenced_code_regex = r"```(?:[a-zA-Z0-9]*\n)?([\s\S]*?)```"
    fenced_matches = re.findall(fenced_code_regex, text)

    # Extract inline code surrounded by single backticks
    inline_code_regex = r"`([^`\n]+)`"
    inline_matches = re.findall(inline_code_regex, text)

    # Combine all code blocks and inline code, initially selecting fenced blocks
    code_blocks = fenced_matches + inline_matches

    # Deduplicate blocks by converting to a set and back to a list
    unique_blocks = list(dict.fromkeys(code_blocks))

    # Rank the blocks based on the presence of specific keywords
    best_block = None
    best_score = 0

    for block in unique_blocks:
        score = 0
        # Increase score if the block contains keywords
        for keyword in keywords:
            if keyword in block.lower():
                score += 1

        # If we find a block with a higher score, select it as the best one
        if score > best_score:
            best_score = score
            best_block = block

    # If no block with flagged words is found, select the last block
    if not best_block:
        best_block = unique_blocks[-1]

    return best_block

if __name__ == "__main__":
    sample_text1 = "```python\n\"\"\"\nModule to perform basic arithmetic operations\n\"\"\"\n\ndef add(a, b):\n    \"\"\"\n    Adds two numbers and returns the result.\n\n    Parameters:\n    a (int, float): The first number.\n    b (int, float): The second number.\n\n    Returns:\n    int, float: The sum of the two numbers.\n    \"\"\"\n    return a + b\n```"
    sample_text2 = "def add(a, b):\n    return a + b"
    sample_text3 = "```python\n\"\"\"\nModule to perform basic arithmetic operations\n\"\"\"\n\ndef add(a, b):\n    \"\"\"\n    Adds two numbers and returns the result.\n\n    Parameters:\n    a (int, float): The first number.\n    b (int, float): The second number.\n\n    Returns:\n    int, float: The sum of the two numbers.\n    \"\"\"\n    return a + b\n"
    sample_text4 = "```python\ndef flatten_list(input_list):\n    if not isinstance(input_list, list):\n        return [input_list]\n    if input_list == []:\n        return []\n    return input_list + flatten_list([item for sublist in input_list for item in sublist])\n```"
    没有用真正的text
    best_block1 = extract_and_select_best_code_block(sample_text1)
    print("Result for sample text 1:")
    print(best_block1)

    best_block2 = extract_and_select_best_code_block(sample_text2)
    print("Result for sample text 2:")
    print(best_block2)

    best_block3 = extract_and_select_best_code_block(sample_text3)
    print("Result for sample text 3:")
    print(best_block3)

    best_block4 = extract_and_select_best_code_block(sample_text4)
    print("Result for sample text 4:")
    print(best_block4)

