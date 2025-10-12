#!/bin/bash

pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --windowed \
  "./WireWarden.py"


# Remove old binary if it exists
[ -f "$HOME/WireWarden/WireWarden" ] && rm "$HOME/WireWarden/WireWarden"

# Create directory if it doesn't exist
mkdir -p "$HOME/WireWarden"

# Copy new binary
cp dist/WireWarden "$HOME/WireWarden/"

# Clean up build folders and files
rm WireWarden.spec
rm -Rf build
rm -Rf dist


# Set variables
APP_NAME="WireWarden"
EXEC_PATH="~/WireWarden/WireWarden"
ICON_PATH="$(pwd)/icon.png"
DESCRIPTION="WireWarden"

# Create the .desktop file
cat << EOF > ~/Desktop/$APP_NAME.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Exec=$EXEC_PATH
Icon=$ICON_PATH
Comment=$DESCRIPTION
Categories=Utility;
Terminal=false
EOF

# Make the .desktop file executable
chmod +x ~/Desktop/$APP_NAME.desktop

# Update the desktop database
#update-desktop-database ~/.local/share/applications

echo ".desktop file created successfully at ~/Desktop/$APP_NAME.desktop"
