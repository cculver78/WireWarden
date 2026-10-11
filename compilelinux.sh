#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="WireWarden"
INSTALL_DIR="$HOME/WireWarden"
EXEC_PATH="$INSTALL_DIR/WireWarden"
ICON_PATH="$INSTALL_DIR/icon.png"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/WireWarden.desktop"
DESKTOP_SHORTCUT="$HOME/Desktop/WireWarden.desktop"

# Run from the directory containing WireWarden.py and icon.png.
if [[ ! -f WireWarden.py || ! -f icon.png ]]; then
  echo "Run this script from the directory containing WireWarden.py and icon.png." >&2
  exit 1
fi

# Build WireWarden.
pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --windowed \
  --icon "./icon.png" \
  "./WireWarden.py"

# Install the binary and icon.
mkdir -p "$INSTALL_DIR" "$DESKTOP_DIR" "$HOME/Desktop"
install -m 755 "dist/WireWarden" "$EXEC_PATH"
install -m 644 "icon.png" "$ICON_PATH"

# Install KDE launcher in the applications directory for Wayland task-manager matching.
cat > "$DESKTOP_FILE" <<EOF_DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Exec=$EXEC_PATH
Icon=$ICON_PATH
Comment=WireWarden
Categories=Utility;
Terminal=false
StartupNotify=true
StartupWMClass=WireWarden
EOF_DESKTOP

chmod +x "$DESKTOP_FILE"
cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
chmod +x "$DESKTOP_SHORTCUT"

# Mark the Desktop shortcut as trusted where supported.
if command -v gio >/dev/null 2>&1; then
  gio set "$DESKTOP_SHORTCUT" metadata::trusted true 2>/dev/null || true
fi

# Refresh the desktop-entry database and KDE Plasma's application cache.
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
  kbuildsycoca6 --noincremental || true
fi

# Remove temporary PyInstaller files.
rm -f "WireWarden.spec"
rm -rf "build" "dist"

echo "WireWarden installed successfully."
echo "Executable: $EXEC_PATH"
echo "Icon:       $ICON_PATH"
echo "KDE launcher: $DESKTOP_FILE"
echo "Desktop shortcut: $DESKTOP_SHORTCUT"
