from flask import Blueprint, request, jsonify
from app.utils import extract_code_from_input, save_code_to_temp, log_info, log_error
from Feedback.send_feedback import send_feedback
from Checks.static_analysis import run_clangtidy_check, run_sonarqube_check
from Checks.dynamic_analysis import run_valgrind_check
from Checks.formal_verification import run_dafny_check
import os
import json

app_routes = Blueprint("app_routes", __name__)

# Supported languages for each tool
clangtidy_lang = ["C", "C++"]
sonarqube_lang = ["Java", "C#", "JavaScript", "TypeScript", "CloudFormation", "Terraform", 
                  "Docker", "Kubernetes", "Helm Charts", "Kotlin", "Ruby", "Go", "Scala", 
                  "Flex", "Python", "PHP", "HTML", "CSS", "XML", "VB.NET"]
valgrind_lang = ["C", "C++", "Fortran", "Ada", "Assembly", "Java", "Python", "Perl"]
dafny_lang = ["C#", "Go", "Python", "Java", "JavaScript"]

RESULTS_FILE = "Results/combined_results.json"

@app_routes.route('/analyze', methods=['POST'])
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

    # Log the analysis completion
    log_info("Code analysis completed successfully.")

    # Return results to the API caller
    return jsonify(results)

@app_routes.route('/feedback', methods=['POST'])
def feedback():
    """Endpoint for sending feedback to the LLM."""
    data = request.get_json()
    model_name = data.get("model_name")
    feedback_data = data.get("feedback_data")

    if not model_name or not feedback_data:
        log_error("Missing model name or feedback data in request.")
        return jsonify({"error": "Model name and feedback data are required"}), 400

    success = send_feedback(feedback_data, model_name)
    if success:
        return jsonify({"message": "Feedback sent successfully."}), 200
    else:
        return jsonify({"error": "Failed to send feedback."}), 500