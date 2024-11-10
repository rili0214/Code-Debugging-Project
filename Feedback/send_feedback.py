import requests
from app.utils import log_info, log_error

def send_feedback(feedback_data, student_id, course_id):
    """Send feedback data to the college feedback API."""
    url = "http://192.168.1.162:5001/feedback"  # Point to the mock server on the second device
    
    payload = {
        "feedback_data": feedback_data,
        "student_id": student_id,
        "course_id": course_id
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            log_info("Feedback sent successfully.")
            return True
        else:
            log_error(f"Failed to send feedback: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        log_error(f"Feedback sending error: {e}")
        return False
