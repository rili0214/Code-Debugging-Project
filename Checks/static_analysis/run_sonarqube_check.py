# curl -X GET 'http://localhost:9000/api/projects/search' -u 'sqa_d0d047345f91bda26804ee916c552c408150acb0'
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

# My sonarqube config for testing, replace with yours
SONARQUBE_URL = 'http://localhost:9000'
SONAR_PROJECT_KEY = 'static-debugging' 
USERNAME = 'admin'
PASSWORD = 'urpassword'                   

def run_sonar_scanner():
    if platform.system() != "Linux":
        print("This script is intended to run on Linux.")
        sys.exit(1)

    # Replace with yours
    sonar_scanner_path = '/mnt/c/Users/taox0/OneDrive/Documents/LLaMa/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner'
    project_dir = '/mnt/c/Users/taox0/OneDrive/Documents/LLaMa/Test_example'

    os.chdir(project_dir)

    try:
        result = subprocess.run([sonar_scanner_path], check=True, text=True, capture_output=True)
        print("SonarQube analysis completed successfully.")
        print("Output:\n", result.stdout)
        return result.returncode == 0
    
    except subprocess.CalledProcessError as e:
        print("An error occurred while running SonarQube analysis.")
        print("Error output:\n", e.stderr)
        return False

def fetch_detailed_report(project_key, username, password):
    metrics = (
    "alert_status,bugs,vulnerabilities,code_smells,coverage,ncloc,complexity,"
    "duplicated_lines_density,duplicated_blocks,security_rating,reliability_rating,"
    "comment_lines_density,line_coverage,branch_coverage,complexity_in_classes,"
    "complexity_in_functions,functions,files,classes,statements,comment_lines,"
    "public_documented_api_density,public_undocumented_api"
    )
    
    components_url = f"{SONARQUBE_URL}/api/components/search?qualifiers=TRK&componentKeys={project_key}"
    measures_url = f"{SONARQUBE_URL}/api/measures/component?component={project_key}&metricKeys={metrics}"

    response = requests.get(components_url, auth=(username, password))
    if response.status_code != 200:
        print(f"Failed to fetch components: {response.status_code} - {response.text}")
        return None
    components = response.json()

    response = requests.get(measures_url, auth=(username, password))
    if response.status_code != 200:
        print(f"Failed to fetch measures: {response.status_code} - {response.text}")
        return None
    measures = response.json()

    report = {
        'components': components.get('components', []),
        'measures': measures['component'].get('measures', [])
    }
    return report


def save_report(report, filename):
    with open(filename, 'w') as f:
        json.dump(report, f, indent=4)
    print(f"Sonarqube report saved to {filename}")

if __name__ == "__main__":
    # Run the SonarQube scanner
    if run_sonar_scanner():
        # Fetch the detailed SonarQube analysis report
        report = fetch_detailed_report(SONAR_PROJECT_KEY, USERNAME, PASSWORD)

        # Save the report
        if report:
            save_report(report, 'sonarqube_report.json')