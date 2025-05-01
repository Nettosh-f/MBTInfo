#!/bin/bash

# Set the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create and activate virtual environment
echo "Creating and activating virtual environment..."
python3 -m venv "$PROJECT_ROOT/venv"
source "$PROJECT_ROOT/venv/bin/activate"

# Install required packages
echo "Installing required packages..."
pip install -r "$PROJECT_ROOT/requirements.txt"

# Run the GUI application
echo "Starting the MBTI application..."
python "$PROJECT_ROOT/src/MBTInfo/gui.py"

# Deactivate the virtual environment
deactivate

echo "MBTI application closed. Virtual environment deactivated."