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
    code = data.get("code")
    dafny_code = data.get("dafny_code")
    language = data.get("language")
    return code, dafny_code, language

def save_code_to_temp(code, language):
    """Save code to a temporary file based on the provided language."""
    ext = "dfy" if language.lower() == "dafny" else language.lower()
    filename = f"{TEMP_DIR}/temp_code_{uuid.uuid4()}.{ext}"
    with open(filename, "w") as file:
        file.write(code)
    return filename

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)