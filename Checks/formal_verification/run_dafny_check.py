import subprocess
import json
import sys

def run_dafny(file_path):
    """
    Run Dafny code from a file, check for verification, and save output to JSON file.
    """
    result = subprocess.run(
        ["/home/xym410102/dafny/Scripts/dafny", "verify", file_path], 
        capture_output=True, 
        text=True
    )

    report = {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "verification_status": "success" if "Dafny program verifier finished with" in result.stdout else "failure"
    }

    #with open("dafny_report.json", "w") as json_file:
        #json.dump(report, json_file, indent=4)
    
    return report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run_dafny_check.py <source_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    # Run Dafny and save report
    report = run_dafny(file_path)

    # Print the report
    print("Dafny Verification Report:")
    print(json.dumps(report, indent=4))