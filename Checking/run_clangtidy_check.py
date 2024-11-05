"""
For C & C++ code. It generates a .json file for later use.
"""
import subprocess
import os
import json
import re
import sys

def run_clang_tidy(file_path, output_file):
    if not os.path.isfile(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return

    command = [
        "clang-tidy",
        file_path,
        "--checks=*,-clang-diagnostic*-warning",  # Ignore all warning checks
        "--",
        "-Werror"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        output = {
            "file": file_path,
            "status": "success" if result.returncode == 0 else "failure",
            "command": " ".join(command),
            "errors": [],
            "warnings": [], 
            "return_code": result.returncode
        }

        pattern = re.compile(r"error: (.*) \[.*\]")  # Only capturing errors

        for line in result.stderr.splitlines():
            match = pattern.search(line)
            if match:
                message = match.group(1)  
                output["errors"].append(message)

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=4)
        print(f"Clangtidy report saved to {output_file}")

    except Exception as e:
        print(f"An error occurred while running clang-tidy: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_clang_tidy.py <path_to_cpp_file> <output_json_file>")
        sys.exit(1)

    cpp_file_path = sys.argv[1]
    output_file = sys.argv[2]
    #project_dir = '/mnt/c/Users/taox0/OneDrive/Documents/LLaMa/Test_example/example.cpp'
    #output_file = 'clangtidy_report.json'
    run_clang_tidy(cpp_file_path, output_file)
    #run_clang_tidy(project_dir, output_file)