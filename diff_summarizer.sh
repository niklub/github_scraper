#!/bin/bash
python get_diff.py "$1" "$2"
if [ $? -eq 0 ] && [ -f "diff.txt" ]; then
    ./llm_summarize diff.txt --output output.md
else
    echo "Error: Failed to generate diff.txt"
    exit 1
fi