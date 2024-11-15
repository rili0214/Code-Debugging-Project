import os
import json
import uuid
import traceback
from flask import Blueprint, request, jsonify
from app.utils import extract_code_from_input, save_code_to_temp, safe_remove, log_info, log_error, cleanup_java_temp_files, calculate_scores
from Checks.static_analysis.run_sonarqube_check import run_sonar_scanner, fetch_detailed_report, SONAR_PROJECT_KEY, USERNAME, PASSWORD
from Checks.static_analysis.run_clangtidy_check import run_clang_tidy
from Checks.static_analysis.run_py_check import run_pystatic_analysis
from Checks.dynamic_analysis.run_valgrind_check import run_valgrind_check
from Checks.formal_verification.run_dafny_check import run_dafny_code

app_routes = Blueprint('app_routes', __name__)

# Define supported languages
python_lang = ["Python"]
clangtidy_lang = ["C", "C++"]
sonarqube_lang = ["Java", "C#", "JavaScript", "TypeScript", "CloudFormation", "Terraform", 
                  "Docker", "Kubernetes", "Helm Charts", "Kotlin", "Ruby", "Go", "Scala", 
                  "Flex", "PHP", "HTML", "CSS", "XML", "VB.NET"]
valgrind_lang = ["C", "C++", "Fortran", "Ada", "Assembly", "Java", "Python", "Perl"]
dafny_lang = ["C#", "Go", "Python", "Java", "JavaScript"]

TEMP_DIR = "temp/code_files"
RESULTS_FILE = "Results/combined_results.json"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

@app_routes.route('/analyze', methods=['POST'])
def analyze_code():
    """API endpoint for analyzing code with improved error handling, concurrency, and security."""
    temp_code_file = None  
    temp_dafny_file = None
    try:
        # Validate JSON input
        if not request.is_json:
            return jsonify({"error": "Invalid JSON format"}), 400
        data = request.get_json()

        print(f"Received data: {data}")

        # Extract and validate input
        mode, model, code, dafny_code, language = extract_code_from_input(data)
        if not code or not language:
            print("Missing code or language")
            return jsonify({"error": "Code and language fields are required"}), 400

        # Tool selection based on language
        run_pystatic = language in python_lang
        run_clangtidy = language in clangtidy_lang
        run_sonarqube = language in sonarqube_lang
        run_valgrind = language in valgrind_lang
        run_dafny = language in dafny_lang

        # Generate unique temp file for each request
        temp_code_file = save_code_to_temp(code, language)
        
        # Results dictionary
        results = {}
        results["model"] = model
        results["generated_code"] = code
        
        # Run analyses
        if run_pystatic:
            print("Running Python static analysis...")
            results["python static analysis"] = run_pystatic_analysis(temp_code_file)

        if run_clangtidy:
            print("Running ClangTidy analysis...")
            results["clang_tidy"] = run_clang_tidy(temp_code_file)

        if run_sonarqube:
            print("Running SonarQube analysis...")
            if run_sonar_scanner():
                report = fetch_detailed_report(SONAR_PROJECT_KEY, USERNAME, PASSWORD)
                results["sonarqube"] = report
            else:
                print("SonarQube scanner execution failed.")

        if mode == "mode_2":
            if run_valgrind:
                print("Running Valgrind analysis...")
                results["valgrind"] = run_valgrind_check(temp_code_file)

            if run_dafny and dafny_code:
                temp_dafny_file = save_code_to_temp(dafny_code, "dfy")
                print("Running Dafny analysis...")
                results["dafny"] = run_dafny_code(temp_dafny_file)
            else:
                results["dafny"] = {"verification_status": "no code provided"}

        results["evaluation_score"] = calculate_scores(results, mode)

        # Write results to file safely
        with open(RESULTS_FILE, "w") as file:
            json.dump(results, file, indent=4)

        log_info("Code analysis completed successfully.")
        return jsonify(results)

    except Exception as e:
        # Log detailed error and return error response
        error_details = traceback.format_exc()
        log_error(f"Error in code analysis: {error_details}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        # Clean up temp files to avoid resource leaks
        if temp_code_file:
            safe_remove(temp_code_file)
        if temp_dafny_file:
            safe_remove(temp_dafny_file)
        cleanup_java_temp_files(TEMP_DIR)