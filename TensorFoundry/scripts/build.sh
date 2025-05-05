#!/bin/bash


DIST_PATH="--distpath ../dist/bin"
WORK_PATH="--workpath ../build"
SPEC_PATH="--specpath ../"
PATHS="--paths=../src"
HIDDEN_IMPORTS="--hidden-import PIL._tkinter_finder"
MAIN_SCRIPT="../src/application.py"
OPTIONS="--onefile --windowed --name TensorFoundry"
ASSETS_FOLDER="../assets"
CONFIG_FILE="../src/*.conf"

# Create the virtual environment
source venv.sh

# Run PyInstaller
../venv/bin/python3 -m PyInstaller $OPTIONS $DIST_PATH $WORK_PATH $SPEC_PATH $PATHS $HIDDEN_IMPORTS $MAIN_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Error: PyInstaller failed! Check the logs above for details."
    exit 1  # Exit with an error code
fi

# Copy assets to dist folder
if [ -d "$ASSETS_FOLDER" ]; then
    echo "📂 Copying assets..."
    cp -r $ASSETS_FOLDER ../dist/assets
    echo "✅ Assets copied successfully!"
else
    echo "⚠️ Warning: Assets folder ($ASSETS_FOLDER) not found, skipping..."
fi

if ls $CONFIG_FILE 1> /dev/null 2>&1; then
    echo "📝 Copying config files..."
    cp $CONFIG_FILE ../dist/bin/
    echo "✅ Config files copied successfully!"
else
    echo "⚠️ Warning: No config files found, skipping..."
fi

deactivate

echo "✅ Build successful! Check the 'dist' folder for the executable."
exit 0  # Exit successfully
