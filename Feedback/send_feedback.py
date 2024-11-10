import requests
from app.utils import log_info, log_error

def send_feedback(feedback_data, model_name):
    """Send feedback data to a specific LLM model."""
    url = f"https://api.llmprovider.com/models/{model_name}/feedback"
    payload = {"feedback": feedback_data}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            log_info("Feedback sent successfully.")
            return True
        else:
            log_error(f"Failed to send feedback: {response.status_code}")
            return False
    except requests.RequestException as e:
        log_error(f"Feedback sending error: {e}")
        return False