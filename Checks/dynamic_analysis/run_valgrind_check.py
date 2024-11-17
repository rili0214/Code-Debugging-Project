import subprocess
import os
import sys
import platform
import json
import re
from datetime import datetime

def run_valgrind_check(file_path):
    _, ext = os.path.splitext(file_path)
    
    if ext in ['.c', '.cpp', '.f', '.ada', '.asm']:
        return run_valgrind_for_compiled(file_path)
    elif ext == '.java':
        return run_valgrind_for_java(file_path)
    elif ext == '.py':
        return run_valgrind_for_interpreter(file_path, 'python3')
    elif ext == '.pl':
        return run_valgrind_for_interpreter(file_path, 'perl')
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def run_valgrind_for_compiled(file_path):
    compiled_program = compile_program(file_path)
    #print(f"Running Valgrind on {compiled_program}")
    command = ['valgrind', '--leak-check=full', './' + compiled_program]
    result = subprocess.run(command, capture_output=True, text=True)
    output_json = process_valgrind_output(result)
    #save_json_output(output_json, file_path, 'valgrind_report.json')
    print("Valgrind analysis completed successfully.")
    return output_json

def compile_program(file_path):
    output_file = 'a.out' if platform.system() != 'Windows' else 'a.exe'
    if file_path.endswith('.cpp'):
        compile_cmd = ['g++', file_path, '-o', output_file]
    elif file_path.endswith('.c'):
        compile_cmd = ['gcc', file_path, '-o', output_file]
    elif file_path.endswith('.f'):
        compile_cmd = ['gfortran', file_path, '-o', output_file]
    elif file_path.endswith('.ada'):
        compile_cmd = ['gnatmake', file_path]
        output_file = file_path.replace('.ada', '')
    else:
        raise ValueError(f"Unsupported language for compilation: {file_path}")
    
    #print(f"Compiling {file_path}")
    subprocess.run(compile_cmd, check=True)
    return output_file

def run_valgrind_for_java(file_path, lib_paths=None):
    # Ensure the file has a .java extension
    if not file_path.endswith('.java'):
        print(f"Error: The file {file_path} is not a Java file.")
        return None

    # Read the code to extract the class name if public
    with open(file_path, 'r') as f:
        code = f.read()

    # Check if there's a public class declaration
    match = re.search(r'public class (\w+)', code)
    if match:
        class_name = match.group(1)
        new_file_path = os.path.join(os.path.dirname(file_path), f"{class_name}.java")
        os.rename(file_path, new_file_path)
        file_path = new_file_path
    
    # Prepend import statement for java.util.*
    code = "import java.util.*;\n" + code
    
    # Write the modified code back to the file
    with open(file_path, 'w') as f:
        f.write(code)

    # Compile the Java file
    try:
        command = ['javac', file_path]
        if lib_paths:
            classpath = ':'.join(lib_paths)  # For Linux/Mac
            # For Windows, replace ':' with ';' in the classpath
            if os.name == 'nt':
                classpath = ';'.join(lib_paths)
            command = ['javac', '-cp', classpath, file_path]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        return None
    
    # Run Valgrind on the Java class
    class_file = file_path.replace('.java', '')
    command = ['valgrind', '--leak-check=full', 'java', class_file]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Valgrind execution failed: {e}")
        return None
    
    output_json = process_valgrind_output(result)
    
    print("Valgrind analysis completed successfully.")
    return output_json


def run_valgrind_for_interpreter(file_path, interpreter):
    #print(f"Running Valgrind on {interpreter} for {file_path}")
    command = ['valgrind', '--leak-check=full', interpreter, file_path]
    result = subprocess.run(command, capture_output=True, text=True)
    output_json = process_valgrind_output(result)
    #save_json_output(output_json, file_path, 'valgrind_report.json')
    print("Valgrind analysis completed successfully.")
    return output_json

def process_valgrind_output(result):
    output = result.stderr
    memory_issues = {
        "uninitialized_value_errors": set(),
        "invalid_read_errors": set(),
        "invalid_write_errors": set(),
        "definitely_lost": set(),
        "indirectly_lost": set(),
        "possibly_lost": set(),
        "still_reachable": set()
    }
    stderr = output.splitlines()

    in_leak_summary = False
    for line in stderr:
        if 'Use of uninitialised value' in line:
            memory_issues["uninitialized_value_errors"].add(line.strip())
        elif 'Invalid read of size' in line:
            memory_issues["invalid_read_errors"].add(line.strip())
        elif 'Invalid write of size' in line:
            memory_issues["invalid_write_errors"].add(line.strip())

        if 'LEAK SUMMARY:' in line:
            in_leak_summary = True
            continue

        if in_leak_summary:
            if 'definitely lost:' in line:
                memory_issues["definitely_lost"].add(line.strip())
            elif 'indirectly lost:' in line:
                memory_issues["indirectly_lost"].add(line.strip())
            elif 'possibly lost:' in line:
                memory_issues["possibly_lost"].add(line.strip())
            elif 'still reachable:' in line:
                memory_issues["still_reachable"].add(line.strip())
            elif 'suppressed:' in line:
                in_leak_summary = False

    # Convert sets back to lists and count errors
    result = {
        "memory_issues": {k: list(v) for k, v in memory_issues.items()},
        "error_count": {k: len(v) for k, v in memory_issues.items()}
    }
    return result

def save_json_output(output_json, file_path, filename):
    result = {
        "file": os.path.basename(file_path),
        "date": datetime.now().isoformat(),
        "results": output_json
    }
    results_dir = 'results'
    os.makedirs(results_dir, exist_ok=True)
    file_path = os.path.join(results_dir, filename)

    with open(file_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)
    print(f"Valgrind report saved to {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run_valgrind_check.py <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]

    if not os.path.exists(source_file):
        print(f"File {source_file} does not exist.")
        sys.exit(1)

    try:
        run_valgrind_check(source_file)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Valgrind: {e}")
    except ValueError as ve:
        print(f"Error: {ve}")