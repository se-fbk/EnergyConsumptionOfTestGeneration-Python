#!/bin/bash

PROJECTS_DIR="running_projects"

for dir in "$PROJECTS_DIR"/*/; do
    if [ -f "$dir/requirements.txt" ]; then
        echo "Setting up environment in: $dir"

        cd "$dir" || continue

        if [ -d "venv" ]; then
            echo "Removing existing virtual environment in $dir"
            rm -rf venv
        fi

        python3 -m venv venv

        # Try to activate the virtual environment
        if ! source venv/bin/activate; then
            echo "Failed to activate virtual environment in $dir"
            {
                echo ""
                echo "Activation error in $dir:"
                echo "------------------------------------------------"
                echo "Failed to activate virtual environment."
                echo "------------------------------------------------"
            } >> "$LOG_FILE"

            cd - > /dev/null
            echo "Removing project directory: $dir"
            rm -rf "$dir"
            continue
        fi

        pip install --upgrade pip > /dev/null 2>&1

        # Temp log file
        TEMP_LOG=$(mktemp)

        # Install requirements and capture output
        if pip install -r requirements.txt > "$TEMP_LOG" 2>&1; then
            echo "Requirements installed successfully in $dir"
        else
            echo "Failed to install requirements in $dir"
            cd - > /dev/null
            deactivate 2>/dev/null
            echo "Removing project directory: $dir"
            rm -rf "$dir"
            rm "$TEMP_LOG"
            continue
        fi

        rm "$TEMP_LOG"
        deactivate
        cd - > /dev/null
    fi
done
