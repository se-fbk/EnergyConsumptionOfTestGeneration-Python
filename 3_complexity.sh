#!/bin/bash

ROOT_DIR="running_projects"

COMPLEXITY_SCRIPT="script/complexity.py"
MATCHES_SCRIPT="script/projects_folder.py"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

OUTPUT_CSV="./complexity_results_${TIMESTAMP}.csv"
MATCHED_CSV="projects-path.csv"

# Step 1: Run matcher script
echo "Running matcher script to generate $MATCHED_CSV"
python3 "$MATCHES_SCRIPT" "$ROOT_DIR"

if [ ! -f "$MATCHED_CSV" ]; then
    echo "Matching CSV not found: $MATCHED_CSV"
    exit 1
fi

# Step 2: Create output file
> "$OUTPUT_CSV"

# Step 3: Loop through CSV
tail -n +2 "$MATCHED_CSV" | while IFS=, read -r project_name matched_path; do
    # Clean quotes if present
    matched_path=$(echo "$matched_path" | tr -d '" \r' | sed 's:/*$::')
    full_path="$ROOT_DIR/$matched_path"
    project_dir="$ROOT_DIR/$project_name"
    venv_path="$project_dir/venv"

    echo "Processing project: $project_name"
    echo " - Code path : $full_path"
    echo " - Venv path : $venv_path"
    echo " - CSV path : $OUTPUT_CSV"

    if [ -f "$venv_path/bin/activate" ]; then
        source "$venv_path/bin/activate"
        echo "Activated venv in: $venv_path"
        pip install radon
        # Run complexity script on matched subfolder
        python3 "$COMPLEXITY_SCRIPT" "$full_path" "$OUTPUT_CSV"
        deactivate
        echo "Deactivated venv"
    else
        echo "!!! No virtualenv found in: $venv_path, skipping."
    fi
    echo "--------------------------------------------"
done

echo "Done. Results saved in: $OUTPUT_CSV"
