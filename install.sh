#!/bin/sh
# Installs Notebooks into your app menu. Your books live in ~/Notebooks.
set -e
dest="$HOME/.local/share/notebooks-app"
mkdir -p "$dest" "$HOME/.local/share/applications"
cp "$(dirname "$0")/app.py" "$(dirname "$0")/index.html" "$dest/"
cat > "$HOME/.local/share/applications/notebooks.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Notebooks
Comment=Academic notes kept as books
Exec=python3 "$dest/app.py"
Icon=accessories-dictionary
Categories=Education;
EOF
echo "Installed. Look for 'Notebooks' in your app menu."
