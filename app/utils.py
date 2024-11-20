import os
import uuid
import glob
import logging
from pathlib import Path
import json
from Checks.rankme.rankme import compute_rankme_score, preprocess_text
from app.routes import dafny_lang

TEMP_DIR = "temp/code_files"

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
    
def extract_code_from_input(data):
    """Extract code and language information from the API input.
    
    Args:
        data (dict): The input data from the API.
    """
    mode = data.get("mode")
    model = data.get("model")
    output = data.get("generated_code")
    dafny_text = data.get("dafny_text")
    language = data.get("language")
    return mode, model, output, dafny_text, language

def save_code_to_temp(code, language):
    """Save code to a temporary file based on the provided language.
    
    Args:
        code (str): The code to save.
        language (str): The language of the code.    
    """
    # Mapping of languages to file extensions
    language = language.lower()
    lang_to_ext = {
        "c++": "cpp",
        "c#": "cs",
        "javascript": "js",
        "typescript": "ts",
        "cloudformation": "yaml",
        "terraform": "tf",
        "kubernetes": "yaml",
        "helm charts": "yaml",
        "html": "html",
        "css": "css",
        "xml": "xml",
        "vb.net": "vb",
        "dafny": "dfy",
        "python": "py",
        "java": "java",
        "ruby": "rb",
        "go": "go",
        "scala": "scala",
        "flex": "mxml",
        "php": "php",
        "docker": "dockerfile",
        "perl": "pl",
        "fortran": "f90",
        "ada": "adb",
        "assembly": "asm"
    }
    
    # Get extension from mapping
    ext = lang_to_ext.get(language.lower(), language.lower())
    
    filename = f"{TEMP_DIR}/temp_code_{uuid.uuid4()}.{ext}"
    with open(filename, "w") as file:
        file.write(code)
    return filename


def safe_remove(file_path):
    """Safely remove a file if it exists.
    
    Args:
        file_path (str): The path to the file to remove.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
    except Exception as e:
        print(f"Failed to remove file {file_path}: {e}")

def cleanup_except_selected(directory, selected_files):
    """
    Remove all files in the directory except the selected ones.
    
    Args:
        directory (str): The directory to clean up.
        selected_files (list): List of file names to keep.
    """
    try:
        for file in glob.glob(os.path.join(directory, "*")):
            if os.path.basename(file) not in selected_files:
                safe_remove(file)
    except Exception as e:
        print(f"Error during cleanup: {e}")       

def log_info(message):
    """Log an information message.
    
    Args:
        message (str): The message to log.
    """
    logger.info(message)

def log_error(message):
    """Log an error message.
    
    Args:
        message (str): The message to log.
    """
    logger.error(message)

def calculate_scores(data, mode, language):
    """
    Calculate scores based on the provided data and mode.
    
    Args:
        data (dict): The data containing analysis results.
        mode (str): The mode of the application.
    """
    static_score, valgrind_score, dafny_score, rankme_score = -1, -1, -1, -1
    
    # Python Static Analysis Scores
    if "python static analysis" in data:
        mypy_score = 10 if "Success" in data["python static analysis"][0]["output"] else 0
        pylint_score = float(data["python static analysis"][1]["output"].split("rated at")[1].split("/10")[0].strip())
        bandit_score = 10 if "No issues identified" in data["python static analysis"][2]["output"] else 0
        static_score = (mypy_score + pylint_score + bandit_score) / 3

    # Clanmgtidy Scores
    if "clang_tidy" in data:
        clangtidy = data.get("clang-tidy", {})
        warnings = len(clangtidy.get("warnings", []))  # Count warnings
        errors = len(clangtidy.get("errors", []))  # Count errors

        if errors > 0:
            static_score = 0  # Fail if there are any errors
        else:
            if warnings == 0:
                static_score = 10  # Perfect score for no warnings
            elif warnings <= 5:
                static_score = max(5, 10 - warnings)  # Slight penalty for up to 5 warnings
            elif warnings <= 15:
                static_score = max(2, 10 - warnings // 2)  # Moderate penalty for 6-15 warnings
            else:
                static_score = 0  # Significant penalty for more than 15 warnings

    # SonarQube Score
    if "sonarqube" in data:
        count = 0
        sonarqube_measures = {
            m["metric"]: float(m["value"]) if m["value"].replace('.', '', 1).isdigit() else 0 
            for m in data["sonarqube"]["measures"]
        }

        if "bugs" in sonarqube_measures:
            bugs_score = 10 if sonarqube_measures["bugs"] == 0 else 0
            static_score += bugs_score
            count += 1

        if "vulnerabilities" in sonarqube_measures:
            vulnerabilities_score = 10 if sonarqube_measures["vulnerabilities"] == 0 else 0
            static_score += vulnerabilities_score
            count += 1

        if "complexity" in sonarqube_measures:
            complexity_score = max(0, 10 - sonarqube_measures.get("complexity", 0))
            static_score += complexity_score
            count += 1

        if "line_coverage" in sonarqube_measures:
            coverage_score = max(0, 10 * sonarqube_measures["line_coverage"] / 100)
            static_score += coverage_score
            count += 1

        if "duplicated_lines_density" in sonarqube_measures:
            duplicated_score = 10 if sonarqube_measures["duplicated_lines_density"] == 0 else 0
            static_score += duplicated_score
            count += 1

        static_score /= count

    if mode == "mode_2":
        # Valgrind Score
        if "valgrind" in data:
            valgrind = data["valgrind"]
            if valgrind["status"] == "failure":
                valgrind_score = 0
            else:
                valgrind_score = 5 if "still reachable" in valgrind["memory_issues"] else 10

        # Dafny Score
        if "dafny" in data:
            dafny_score = 10 if "success" in data["dafny"]["verification_status"] else 0

        # Rankme Score
        split_texts = preprocess_text(data["generated_code"])
        rankme_score = compute_rankme_score(split_texts)
        
    if static_score != -1 and valgrind_score != -1 and dafny_score != -1 and rankme_score != -1:
        final_score = (static_score * 0.4 + valgrind_score * 0.3 + dafny_score * 0.2 + rankme_score * 0.1)
    elif static_score != -1 and valgrind_score != -1 and dafny_score != -1:
        final_score = (static_score * 0.4 + valgrind_score * 0.3 + dafny_score * 0.3) 
    elif static_score != -1 and valgrind_score != -1:
        final_score = (static_score * 0.7 + valgrind_score * 0.3) 
    elif static_score != -1 and dafny_score != -1:
        final_score = (static_score * 0.7 + dafny_score * 0.3)
    # Final Weighted Score
    if mode == "mode_1":
        return {"stsatic_analysis": static_score, "final_score": static_score}
    else:
        return {
            "stsatic_analysis_score": static_score,
            "dynamic_analysis_score": valgrind_score,
            "formal_verification_score": dafny_score,
            "rankme_score": rankme_score,
            "final_score": final_score,
            "Note":"-1 indicates current method is not available"
        }

if __name__ == "__main__":
    data = Path(__file__).parent.parent / 'Results' / 'combined_results.json'
    with open(data, 'r') as f:
        data = json.load(f)
    scores = calculate_scores(data=data, mode="mode_2")
    print(scores)