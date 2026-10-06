#!/bin/bash

set -e

APP_NAME="WireWarden"
INSTALL_DIR="$HOME/WireWarden"
EXEC_PATH="$INSTALL_DIR/WireWarden"
ICON_PATH="$INSTALL_DIR/icon.png"
DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"

# Build WireWarden
pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --windowed \
  "./WireWarden.py"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Remove old binary if it exists
rm -f "$EXEC_PATH"

# Copy new binary
cp "dist/WireWarden" "$EXEC_PATH"

# Copy icon
cp "icon.png" "$ICON_PATH"

# Create the .desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Exec=$EXEC_PATH
Icon=$ICON_PATH
Comment=WireWarden
Categories=Utility;
Terminal=false
EOF

# Make launcher executable
chmod +x "$DESKTOP_FILE"

# Mark launcher as trusted for GNOME
gio set "$DESKTOP_FILE" metadata::trusted true

# Clean up PyInstaller files
rm -f "WireWarden.spec"
rm -rf "build"
rm -rf "dist"

echo "WireWarden installed successfully."
echo "Executable: $EXEC_PATH"
echo "Icon:       $ICON_PATH"
echo "Launcher:   $DESKTOP_FILE"
