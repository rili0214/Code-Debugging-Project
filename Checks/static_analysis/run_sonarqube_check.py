"""
    For other langs code, like Java, Javascript, PHP .etc. It generates a .json file for later use.
"""
import platform
import sys
import subprocess
import requests
import json
import os
from requests.auth import HTTPBasicAuth

# SonarQube configuration for testing; replace with your actual credentials
SONARQUBE_URL = ''
SONAR_PROJECT_KEY = ''
USERNAME = ''
PASSWORD = ''

def run_sonar_scanner():
    """Runs the SonarQube scanner and handles errors and outputs."""

    if platform.system() != "Linux":
        print("This script is intended to run on Linux.")
        sys.exit(1)

    # Path configurations; replace with your paths
    sonar_scanner_path = 'path to sonar-scanner'
    project_dir = 'path to code_files'

    # Check if paths are correct
    if not os.path.isfile(sonar_scanner_path):
        print(f"Sonar scanner path '{sonar_scanner_path}' is invalid.")
        return False
    if not os.path.isdir(project_dir):
        print(f"Project directory '{project_dir}' is invalid.")
        return False
    
    original_dir = os.getcwd()

    os.chdir(project_dir)

    try:
        #result = subprocess.run([sonar_scanner_path], check=True, text=True, capture_output=True)
        subprocess.run([sonar_scanner_path], check=True, text=True, capture_output=True)
        print("SonarQube analysis completed successfully.")
        #print("Output:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("An error occurred while running SonarQube analysis.")
        print("Error output:\n", e.stderr)
    except FileNotFoundError:
        print(f"Sonar scanner not found at path '{sonar_scanner_path}'")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        os.chdir(original_dir)

    return False

def fetch_detailed_report(project_key, username, password):
    """Fetches the SonarQube analysis report for the given project key."""
    
    metrics = (
        "alert_status,bugs,vulnerabilities,code_smells,coverage,ncloc,complexity,"
        "duplicated_lines_density,duplicated_blocks,security_rating,reliability_rating,"
        "comment_lines_density,line_coverage,branch_coverage,complexity_in_classes,"
        "complexity_in_functions,functions,files,classes,statements,comment_lines,"
        "public_documented_api_density,public_undocumented_api"
    )

    components_url = f"{SONARQUBE_URL}/api/components/search?qualifiers=TRK&componentKeys={project_key}"
    measures_url = f"{SONARQUBE_URL}/api/measures/component?component={project_key}&metricKeys={metrics}"

    try:
        # Fetch components
        response = requests.get(components_url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        components = response.json().get('components', [])
        if not components:
            print(f"No components found for project key '{project_key}'")
            return None

        # Fetch measures
        response = requests.get(measures_url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        measures = response.json().get('component', {}).get('measures', [])
        if not measures:
            print(f"No measures found for project key '{project_key}'")
            return None

        report = {
            'components': components,
            'measures': measures
        }
        return report

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching SonarQube report: {http_err}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to SonarQube server. Please check the server status and URL.")
    except requests.exceptions.Timeout:
        print("Request to SonarQube server timed out.")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred while fetching SonarQube report: {req_err}")
    except json.JSONDecodeError:
        print("Failed to parse the JSON response from SonarQube.")

    return None

def save_report(report, filename):
    """Saves the SonarQube report to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"SonarQube report saved to '{filename}'")
    except IOError as io_err:
        print(f"Failed to write report to '{filename}': {io_err}")
    except Exception as e:
        print(f"Unexpected error while saving report: {e}")

if __name__ == "__main__":
    if run_sonar_scanner():
        report = fetch_detailed_report(SONAR_PROJECT_KEY, USERNAME, PASSWORD)
        if report:
            save_report(report, 'sonarqube_report.json')
        else:
            print("Failed to retrieve the report from SonarQube.")
    else:
        print("SonarQube scanner execution failed.")