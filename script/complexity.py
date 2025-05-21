import os
import csv
import sys
from radon.complexity import cc_visit, cc_rank

def compute_complexity(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        blocks = cc_visit(code)
        if blocks:
            avg = sum(b.complexity for b in blocks) / len(blocks)
            return round(avg, 2), cc_rank(avg), "ok"
        else:
            return 0.0, cc_rank(0.0), "ok"
    except Exception as e:
        return 99999999, "F", str(e)

def analyze_project(root_dir):
    project_name = os.path.basename(os.path.abspath(root_dir))
    results = []

    for dirpath, _, files in os.walk(root_dir):

        # Skip venv and __pycache__
        if any(x in dirpath for x in ['venv', '__pycache__', 'pynguin', 'tests', 'test']):            
            continue

        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(dirpath, file)
                avg_complexity, rank, status = compute_complexity(file_path)
                module_name = os.path.relpath(file_path, root_dir)
                results.append((os.path.dirname(root_dir), project_name, module_name, avg_complexity, rank, status))

    return results

def append_to_csv(results, output_file):
    file_exists = os.path.exists(output_file)
    header = ['root_dir', 'project', 'module', 'avg_complexity', 'rank', 'status']

    with open(output_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerows(results)

    if not file_exists:
        print(f"Created new file: {output_file}")
    print(f"Appended {len(results)} rows to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 complexity.py /path/to/project /path/to/output.csv")
        sys.exit(1)

    folder = sys.argv[1]
    csv_path = sys.argv[2]
    print(f"- Analyzing project: {folder}")
    print(f"- Output CSV: {csv_path}")
    results = analyze_project(folder)
    append_to_csv(results, csv_path)
