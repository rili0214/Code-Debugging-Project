import os
import uuid
import logging

TEMP_DIR = "temp/code_files"

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_code_from_input(data):
    """Extract code and language information from the API input."""
    model = data.get("model")
    code = data.get("code")
    dafny_code = data.get("dafny_code")
    language = data.get("language")
    return model, code, dafny_code, language

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