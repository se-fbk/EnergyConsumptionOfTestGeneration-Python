import csv
import os
import subprocess
import sys
import parameters
from datetime import datetime

LOG_FILE = "setup_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(full_message + '\n')

def setup_environments(report_csv, folder):

    with open(report_csv, mode='r', newline='') as file:
        rows = list(csv.DictReader(file))
        total = len(rows)

    # Read CSV Report
    with open(report_csv, mode='r', newline='') as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            # Extract project name and requirements status
            project = row['Project']
            has_requirements = row['Requirements'].lower() == 'true'

            project_path = os.path.join(folder, project)
            log("--------------------------------------------------------")
            log(f"[{index}/{total}] Processing project: {project}")

            if has_requirements and os.path.isdir(project_path):
                log(f"[+] Setting up environment for: {project}")

                # Create venv path
                venv_path = os.path.join(project_path, 'venv')

                if os.path.exists(venv_path):
                    subprocess.run(['rm', '-rf', venv_path])

                # Create virtual environment
                result = subprocess.run([sys.executable, '-m', 'venv', venv_path])

                log(f"    → Created virtual environment: {'OK' if result.returncode == 0 else 'FAILED'}")

                # Path to pip inside venv
                pip_path = os.path.join(venv_path, 'Scripts' if os.name == 'nt' else 'bin', 'pip')

                # Find all requirement files
                requirement_files = [
                    os.path.join(project_path, f)
                    for f in os.listdir(project_path)
                    if 'requirement' in f.lower()
                ]

                if requirement_files:
                    for req_file in requirement_files:
                        log(f"    → Installing from {req_file}")
                        subprocess.run([pip_path, 'install', '-r', req_file])
                        subprocess.run([pip_path, 'install', parameters.PYNGUIN])
                        log(f"    → Installed dependencies and Pynguin")
                else:
                    log(f"    No requirements file found in {project_path}, even though CSV says so.")
            else:
                if not has_requirements:
                    log(f"    Skipping {project}: 'Requirements' is False in CSV.")
                elif not os.path.isdir(project_path):
                    log(f"    Skipping {project}: folder not found at {project_path}")

if __name__ == "__main__":

    projects = parameters.PROJECTS
    report_csv = parameters.REPORT

    # Reset log file
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("===== Environment Setup Log =====\n\n")

    setup_environments(report_csv, projects)
