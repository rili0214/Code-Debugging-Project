import os
import uuid
import glob
import logging
import json
from Checks.rankme.rankme import compute_rankme_score, preprocess_text

TEMP_DIR = "temp/code_files"

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_code_from_input(data):
    """Extract code and language information from the API input."""
    mode = data.get("mode")
    model = data.get("model")
    code = data.get("code")
    dafny_code = data.get("dafny_code")
    language = data.get("language")
    return mode, model, code, dafny_code, language

def save_code_to_temp(code, language):
    """Save code to a temporary file based on the provided language."""
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
    
    # Get extension from mapping, default to lowercase of language if not mapped
    ext = lang_to_ext.get(language.lower(), language.lower())
    
    filename = f"{TEMP_DIR}/temp_code_{uuid.uuid4()}.{ext}"
    with open(filename, "w") as file:
        file.write(code)
    return filename


def safe_remove(file_path):
    """Safely remove a file if it exists."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        log_error(f"Failed to remove file {file_path}: {e}")

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def cleanup_java_temp_files(directory):
    # Remove all .java and .class files in the specified directory
    for temp_file in glob.glob(os.path.join(directory, "*.java")) + glob.glob(os.path.join(directory, "*.class")):
        try:
            os.remove(temp_file)
            print(f"Removed temporary file: {temp_file}")
        except OSError as e:
            print(f"Error removing file {temp_file}: {e}")

def calculate_scores(data, mode):
    static_score, valgrind_score, dafny_score, rankme_score = 0, 0, 0, 0
    # Python Static Analysis Scores
    if "python static analysis" in data:
        mypy_score = 10 if "Success" in data["python static analysis"][0]["output"] else 0
        pylint_score = float(data["python static analysis"][1]["output"].split("rated at")[1].split("/10")[0].strip())
        bandit_score = 10 if "No issues identified" in data["python static analysis"][2]["output"] else 0
        static_score = (mypy_score + pylint_score + bandit_score) / 3

    # Clanmgtidy Scores
    if "clang-tidy" in data:
        clangtidy = data.get("clang-tidy", {})
        warnings = clangtidy.get("warnings", 0)
        errors = clangtidy.get("errors", 0)
        if errors > 0:
            static_score = 0  
        elif warnings <= 5:
            static_score = 10 - warnings  
        elif warnings <= 15:
            static_score = max(5, 10 - warnings)  
        else:
            static_score = 0  

    # SonarQube Score
    if "sonarqube" in data:
        sonarqube_measures = {m["metric"]: float(m["value"]) for m in data["sonarqube"]["measures"]}
        bugs_score = 10 if sonarqube_measures["bugs"] == 0 else 0
        vulnerabilities_score = 10 if sonarqube_measures["vulnerabilities"] == 0 else 0
        complexity_score = max(0, 10 - sonarqube_measures["complexity"])
        coverage_score = max(0, 10 * sonarqube_measures["line_coverage"] / 100)
        duplicated_score = 10 if sonarqube_measures["duplicated_lines_density"] == 0 else 0
        static_score = (bugs_score + vulnerabilities_score + complexity_score + coverage_score + duplicated_score) / 5

    if mode == "mode_2":
        # Valgrind Score
        valgrind = data["valgrind"]
        valgrind_score = 5 if "still reachable" in valgrind["memory_issues"] else 10

        # Dafny Score
        dafny_score = 10 if "success" in data["dafny"]["verification_status"] else 0

        # Rankme Score
        split_texts = preprocess_text(data["generated_code"])
        rankme_score = compute_rankme_score(split_texts)

    final_score = (static_score * 0.4 + valgrind_score * 0.3 + dafny_score * 0.2 + rankme_score * 0.1) if mode == "mode_2" else static_score
    
    # Final Weighted Score
    if mode == "mode_1":
        return {"stsatic_analysis": static_score, "final_score": final_score}
    else:
        return {
            "stsatic_analysis_score": static_score,
            "dynamic_analysis_score": valgrind_score,
            "formal_veriofication_score": dafny_score,
            "rankme_score": rankme_score,
            "final_score": final_score
        }

