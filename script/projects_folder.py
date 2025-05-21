import os
import re
import sys
import csv

OUTPUT_CSV = "./projects-path.csv"

def normalize_name(name):
    return re.sub(r'[^a-z]', '', name.lower())

def is_valid(entry_name):
    return 'test' not in entry_name.lower() and '.egg-info' not in entry_name.lower()

def find_correspondence(outer_folder):
    outer_name = os.path.basename(os.path.abspath(outer_folder))
    normalized_outer = normalize_name(outer_name)

    matches = []
    for entry in os.listdir(outer_folder):
        entry_path = os.path.join(outer_folder, entry)
        if os.path.isdir(entry_path) and is_valid(entry):
            normalized_entry = normalize_name(entry)
            if normalized_outer in normalized_entry:
                matches.append(entry)
    return matches

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 projects_path.py /path/to/running_projects")
        sys.exit(1)

    root_dir = os.path.abspath(sys.argv[1]) # running_projects folder
    print(f"- Scanning projects in: {root_dir}")

    valid_projects = []

    for outer in sorted(os.listdir(root_dir)):
       
        outer_path = os.path.join(root_dir, outer)  # project folder
        if not os.path.isdir(outer_path):
            continue

        matches = find_correspondence(outer_path)

        if len(matches) == 1:
            rel_path = f"{outer}/{matches[0]}" # build path (/project_name/folder)
            valid_projects.append((outer, rel_path))
            #print(f"- {outer} => Match: {rel_path}")
        else:
            reason = "none" if not matches else "multiple"
            #print(f"!!! {outer} => Excluded (match: {reason})")

    # CSV
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['project', 'matched_path'])
        writer.writerows(valid_projects)

    print(f"- Done. {len(valid_projects)} valid projects written to: {OUTPUT_CSV}")
