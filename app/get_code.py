import re

import re

def extract_and_select_best_code_block(text):
    """
    Extracts the most relevant code block from text containing multiple code snippets and explanations.
    Handles cases where code blocks follow specific keywords like 'revised', 'updated', etc.
    """
    if not text or not isinstance(text, str):
        return ""

    # Keywords indicating preferred code
    keywords = [
        "correct",
        "revised",
        "updated",
        "optimized",
        "refactored",
    ]

    # Regex for extracting code blocks enclosed by triple backticks
    code_block_regex = r"```(?:[a-zA-Z0-9]*\n)?([\s\S]*?)```"
    code_blocks = re.findall(code_block_regex, text, re.VERBOSE)

    # Fallback regex to extract plain code snippets
    plain_code_regex = r"""
        (?:(?:^|\n)[ \t]*)                  # Line start or newline, optionally indented
        (?:def\s+\w+\s*\([^)]*\):\s*        # Match Python function definition
        |class\s+\w+\s*                     # Match class definition
        |for\s+\w+\s+in\s+.*?:\s*           # Match 'for' loops
        |while\s+.*?:\s*                    # Match 'while' loops
        |if\s+.*?:\s*                       # Match 'if' statements
        |try\s*:\s*                         # Match 'try' blocks
        |except\s+.*?:\s*                   # Match 'except' blocks
        |finally\s*:\s*                     # Match 'finally' blocks
        |with\s+.*?:\s*                     # Match 'with' statements
        |return\s+.*?(?:\n|$))              # Match 'return' statements
        (?:\s*.*(?:\n|$))*                  # Match the rest of the block
    """
    if not code_blocks:
        code_blocks = re.findall(plain_code_regex, text, re.VERBOSE | re.DOTALL)

    # Match explanations with keywords
    explanation_regex = rf"({'|'.join(keywords)})[\s\S]*?(?=```|$)"
    explanations = re.finditer(explanation_regex, text, re.IGNORECASE)

    # Pair explanations with code blocks
    for explanation in explanations:
        explanation_end = explanation.end()
        for code in code_blocks:
            code_start = text.find(code)
            if code_start > explanation_end:  # Ensure code appears after the explanation
                return code.strip()

    # If no matches found, return the first valid code block
    return code_blocks[0].strip()