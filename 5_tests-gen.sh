#!/bin/bash

# Crea la directory di output con timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="./gen-results_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

TIMEOUT=60
RUNS=1

INPUT_CSV="high-low-ccn-modules.csv"
ALGORITHMS=("DYNAMOSA")

BASE_DIR="$(pwd)"

while IFS=, read -r root_dir module avg_ccn ccn_group
do  
    if [ "$root_dir" == "root_dir" ]; then
        echo "Skipping header line"
        continue
    fi

    for algo in "${ALGORITHMS[@]}"
    do 
        if ! python3 script/test_generation.py "$root_dir" "$module" "$OUTPUT_DIR" "$algo" "$TIMEOUT" "$RUNS"; then
            echo "[ERROR] Failed for $module"
            continue
        fi
    done    

done < $INPUT_CSV