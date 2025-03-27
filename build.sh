#!/bin/bash

# Exit on error
set -e

echo "Building kokorofile..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
uv venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller kokorofile.spec

echo "Build complete! Binary is available in dist/kokorofile"
echo "Note: Make sure espeak-ng is installed on your system:"
echo "  Ubuntu/Debian: sudo apt-get install espeak-ng"
echo "  Fedora: sudo dnf install espeak-ng"
echo "  Arch Linux: sudo pacman -S espeak-ng" 