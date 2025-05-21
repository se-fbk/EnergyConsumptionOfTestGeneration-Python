#!/bin/bash

BASE_DIR="./Python_projects_flaky"
RUNNING_DIR="./running_projects"

# Create directory
mkdir -p "$RUNNING_DIR"

count=0

for dir in "$BASE_DIR"/*/; do
    if [ -d "$dir" ]; then
        if [ -f "$dir/requirements.txt" ]; then
            ((count++))
            cp -r "$dir" "$RUNNING_DIR" # Copy the project to the running directory
        fi
    fi
done

echo "Number of projects with requirements.txt: $count"
echo "Projects copied to: $RUNNING_DIR"
