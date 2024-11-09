import os
import json
import uuid
import subprocess
from Checks.static_analysis import run_clangtidy_check, run_sonarqube_check
from Checks.dynamic_analysis import run_valgrind_check
from Checks.formal_verification import run_dafny_check
from flask import Flask, request, jsonify

app = Flask(__name__)

# Supported languages for each tool
clangtidy_lang = ["C", "C++"]
sonarqube_lang = ["Java", "C#", "JavaScript", "TypeScript", "CloudFormation", "Terraform", 
                  "Docker", "Kubernetes", "Helm Charts", "Kotlin", "Ruby", "Go", "Scala", 
                  "Flex", "Python", "PHP", "HTML", "CSS", "XML", "VB.NET"]
valgrind_lang = ["C", "C++", "Fortran", "Ada", "Assembly", "Java", "Python", "Perl"]
dafny_lang = ["C#", "Go", "Python", "Java", "JavaScript"]

# Directory for storing temporary code files
TEMP_DIR = "temp/code_files"
RESULTS_FILE = "results/combined_results.json"

# Ensure temp and results directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("results", exist_ok=True)

def extract_code_from_input(data):
    """Extract code and language information from the API input."""
    code = data.get("code")
    dafny_code = data.get("dafny_code")
    language = data.get("language")
    return code, dafny_code, language

def save_code_to_temp(code, language):
    """Save code to a temporary file based on the provided language."""
    filename = f"{TEMP_DIR}/temp_code_{uuid.uuid4()}.{language.lower()}"
    with open(filename, "w") as file:
        file.write(code)
    return filename

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Main API endpoint for analyzing code."""
    data = request.get_json()
    code, dafny_code, language = extract_code_from_input(data)
    
    # Determine which checks to run
    run_clangtidy = language in clangtidy_lang
    run_sonarqube = language in sonarqube_lang
    run_valgrind = language in valgrind_lang
    run_dafny = language in dafny_lang
    
    # Save code to a temporary file for analysis
    temp_code_file = save_code_to_temp(code, language)
    results = {}

    # Run clang-tidy if applicable
    if run_clangtidy:
        results["clang_tidy"] = run_clangtidy_check(temp_code_file)
    
    # Run SonarQube if applicable
    if run_sonarqube:
        results["sonarqube"] = run_sonarqube_check(temp_code_file, language)
    
    # Run Valgrind if applicable
    if run_valgrind:
        results["valgrind"] = run_valgrind_check(temp_code_file)
    
    # Run Dafny if applicable
    if run_dafny:
        temp_dafny_file = save_code_to_temp(dafny_code, "dfy")
        results["dafny"] = run_dafny_check(temp_dafny_file)
        os.remove(temp_dafny_file)

    # Save results to a JSON file
    with open(RESULTS_FILE, "w") as file:
        json.dump(results, file, indent=4)

    # Remove temporary files
    os.remove(temp_code_file)

    # Return results to the API caller
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)