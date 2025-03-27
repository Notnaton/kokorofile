#!/bin/bash

# Exit on error
set -e

echo "Building kokorofile..."

# Run the Cosmopolitan build script
./scripts/cosmo.sh

echo "Build complete! Binary is available in dist/kokorofile"
echo "Note: This is a portable binary that includes all dependencies."
echo "      No additional installation is required." 