#!/bin/bash

VENV_DIR="../venv"
SRC_DIR="../src"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found! Creating one..."
    source venv.sh
fi

# Activate the venv and run
source "$VENV_DIR/bin/activate"
PYTHONPATH=$SRC_DIR python3 $SRC_DIR/application.py

# Deactivate the virtual environment after execution
deactivate

echo "Virtual environment deactivated, script execution complete."
