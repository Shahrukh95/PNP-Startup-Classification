import re
import ast

def extract_list(input_string):
    # Regular expression to match Python-style lists
    list_pattern = r"\[.*?\]"
    match = re.search(list_pattern, input_string)
    if match:
        try:
            return ast.literal_eval(match.group())
        except (SyntaxError, ValueError):
            # Return an empty list if the extracted string isn't a valid Python list
            return []
    return []  # Return empty list