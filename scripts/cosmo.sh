#!/bin/sh
set -eux

PREV="$(pwd)"
DIR="$(mktemp -d)"

# Copy our Python files
cp kokorofile.py "$DIR"

# Create the .args file
cd "$DIR"
printf -- '-m\nkokorofile\n...' > .args

# Download required binaries
wget https://cosmo.zip/pub/cosmos/bin/python
wget https://cosmo.zip/pub/cosmos/bin/zip
chmod +x python
chmod +x zip

# Compile Python files
./python -m compileall -b kokorofile.py

# Create Lib directory and copy files
mkdir Lib
cp kokorofile.pyc Lib/

# Create the final binary
cp python kokorofile.com
./zip -r kokorofile.com Lib .args

# Copy back to original directory
cd "$PREV"
cp "$DIR"/kokorofile.com dist/kokorofile

echo "✔ Built Cosmopolitan APE: dist/kokorofile"
