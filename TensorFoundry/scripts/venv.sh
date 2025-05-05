#!/bin/bash

VENV_DIR="../venv"

# Create the virtual environment
python3 -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install dependencies from requirements.txt
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
else
    echo "requirements.txt not found!"
fi

echo "Virtual environment '$VENV_DIR' is set up and activated."
