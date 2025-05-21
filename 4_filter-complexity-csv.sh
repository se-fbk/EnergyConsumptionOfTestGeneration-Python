#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: ./4_filter-complexity-csv.sh /path/to/complexity-results-file.csv"
    exit 1
fi

CSV_FILE="$1"

if [ ! -f "$CSV_FILE" ]; then
    echo "Error: file '$CSV_FILE' not found."
    exit 1
fi

python3 script/filter_complexity.py "$CSV_FILE"

