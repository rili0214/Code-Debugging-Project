import subprocess
import os
import json

def run_mypy(file_path):
    """Runs mypy analysis on a Python file and returns the output."""
    try:
        result = subprocess.run(
            ["mypy", "--ignore-missing-imports", file_path],
            capture_output=True,
            text=True
        )
        return {"tool": "mypy", "output": result.stdout}
    except FileNotFoundError:
        return {"tool": "mypy", "output": "mypy not found."}
    except Exception as e:
        return {"tool": "mypy", "output": f"mypy failed: {e}"}

def run_pylint(file_path):
    """Runs pylint analysis on a Python file and returns the output."""
    try:
        result = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True
        )
        return {"tool": "pylint", "output": result.stdout}
    except FileNotFoundError:
        return {"tool": "pylint", "output": "pylint not found."}
    except Exception as e:
        return {"tool": "pylint", "output": f"pylint failed: {e}"}

def run_bandit(file_path):
    """Runs bandit analysis on a Python file and returns the output."""
    try:
        result = subprocess.run(
            ["bandit", "-r", file_path],
            capture_output=True,
            text=True
        )
        return {"tool": "bandit", "output": result.stdout}
    except FileNotFoundError:
        return {"tool": "bandit", "output": "bandit not found."}
    except Exception as e:
        return {"tool": "bandit", "output": f"bandit failed: {e}"}

def save_analysis_results(results, analysis_output_path):
    """Saves analysis results to a JSON file."""
    try:
        with open(analysis_output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Static analysis results saved to '{analysis_output_path}'")
    except IOError as e:
        print(f"Failed to write analysis results to '{analysis_output_path}': {e}")
    except Exception as e:
        print(f"Unexpected error while saving analysis results: {e}")

def run_pystatic_analysis(file_path):
    """
    Runs static analysis using mypy, pylint, and bandit on the specified file.
    The results are saved in a JSON file for later use.
    """
    results = []

    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        return
    
    results.append(run_mypy(file_path))
    results.append(run_pylint(file_path))
    results.append(run_bandit(file_path))

    #save_analysis_results(results, analysis_output_path)
    return results

if __name__ == "__main__":
    run_pystatic_analysis()
