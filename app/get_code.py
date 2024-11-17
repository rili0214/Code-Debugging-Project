import re

def extract_and_select_best_code_block(text):
    """
    Extracts the most relevant code block from a text containing multiple code snippets and explanations.
    Stops at the first valid match and returns the entire code block, ignoring further text.
    """
    if not text or not isinstance(text, str):
        return ""

    # Keywords indicating the preferred code block
    keywords = [
        "correct",
        "revised",
        "updated",
        "optimized",
        "refactored",
    ]

    # Extract code blocks surrounded by triple backticks
    code_block_regex = r"```(?:[a-zA-Z0-9]*\n)?([\s\S]*?)```"
    code_blocks = re.findall(code_block_regex, text, re.VERBOSE)

    # If no backtick-enclosed blocks found, fallback to plain detection
    if not code_blocks:
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
        code_blocks = re.findall(plain_code_regex, text, re.VERBOSE | re.DOTALL)

    if not code_blocks:
        return ""

    # Find explanations with keywords and associate them with code blocks
    explanations_with_keywords = []
    for keyword in keywords:
        explanation_regex = rf"{keyword}.*?(?=\ndef|\nclass|for\s+\w+\s+in|while\s+|if\s+|try\s*:\s*|except\s+|finally\s*:\s*|with\s+|return\s+|$)"
        matches = re.finditer(explanation_regex, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            explanations_with_keywords.append((match.start(), match.end()))

    # Rank code blocks by proximity to explanations with keywords
    if explanations_with_keywords:
        best_code = None
        best_distance = float("inf")
        for start, end in explanations_with_keywords:
            for code in code_blocks:
                code_start = text.find(code)
                code_end = code_start + len(code)
                if code_start > start and code_end < end:  # Ensure code appears after the explanation
                    return code.strip()  # Return the whole code block directly

    # If no code blocks are associated with keywords, return the first complete code block found
    return code_blocks[0].strip()


# Test cases
if __name__ == "__main__":
    sample_text1 = "```python\ndef add(a, b):\n    return a + b\n```"
    sample_text2 = "def twosum(nums, target):\n    nums.sort()\n    left, right = 0, len(nums) - 1\n    while left < right:\n        current_sum = nums[left] + nums[right]\n        if current_sum == target:\n            return [left, right]\n        elif current_sum < target:\n            left += 1\n        else:\n            right -= 1\n    return []"
    sample_text3 = "```python\ndef flatten_list_recursive(input_list):\n    result = []\n    for i in input_list:\n        if isinstance(i, list):\n            result.extend(flatten_list_recursive(i))\n        else:\n            result.append(i)\n    return result\n```"
    sample_text4 = """def add(a, b):\n    return a + b\n\n```python\ndef multiply(a, b):\n    return a * b\n```\n\nThis is some text.\n```python\ndef divide(a, b):\n    if b == 0:\n        raise ValueError(\"Cannot divide by zero\")\n    return a / b\n```"""

    # Your provided test case
    sample_text5 = """``` CODE.\n```python\ndef flatten_list(input_list):\n    if not isinstance(input_list, list):\n        return [input_list]\n    if input_list == []:\n        return []\n    return input_list + flatten_list([item for sublist in input_list for item in sublist])\n```\nThe provided code attempts to flatten a list that may contain nested lists. However, it does not correctly handle the nesting because it only attempts to flatten the first element. A correct flattening approach would involve recursion or using a library function designed for this purpose, like `itertools.chain.from_iterable`. Here is a revised version using recursion:\n\n```python\ndef flatten_list_recursive(input_list):\n    result = []\n    for i in input_list:\n        if isinstance(i, list):\n            result.extend(flatten_list_recursive(i))\n        else:\n            result.append(i)\n    return result\n```\nThis recursive solution checks each item in the input list. If the item is an instance of a list, it recursively flattens that sublist and extends the result list with the flattened sublist. If the item is not a list, it appends the item directly to the result list. This method will correctly handle lists of arbitrary nesting."""

    sample_text6 = """def twosum(nums, target):\n    nums.sort()\n    left, right = 0, len(nums) - 1\n    while left < right:\n        current_sum = nums[left] + nums[right]\n        if current_sum == target:\n            return [left, right]\n        elif current_sum < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n def twosum(nums, target):\n    nums.sort()\n    left, right = 0, len(nums) - 1\n    while left < right:\n        current_sum = nums[left] + nums[right]\n        if current_sum == target:\n            return [left, right]\n        elif current_sum < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n def twosum(nums, target):\n    nums.sort()\n    left, right = 0, len(nums) - 1\n    result = []\n    while left < right:\n        current_sum = nums[left] + nums[right]\n        if current_sum == target:\n            result = [left, right]\n            break\n        elif current_sum < target:\n            left += 1\n        else:\n            right -= 1\n    return result\n def twosum_efficient(nums, target):\n    num_indices = {num: index for index, num in enumerate(nums)}\n    for num in nums:\n        complement = target - num\n        if complement in num_indices and num_indices[complement] != num_indices[num]:\n            return [num_indices[num], num_indices[complement]]\n    return []"""

    print("Result for sample text 1:")
    print(extract_and_select_best_code_block(sample_text1))
    print("\nResult for sample text 2:")
    print(extract_and_select_best_code_block(sample_text2))
    print("\nResult for sample text 3:")
    print(extract_and_select_best_code_block(sample_text3))
    print("\nResult for sample text 4:")
    print(extract_and_select_best_code_block(sample_text4))
    print("\nResult for sample text 5:")
    print(extract_and_select_best_code_block(sample_text5))
    print("\nResult for sample text 6:")
    print(extract_and_select_best_code_block(sample_text6))