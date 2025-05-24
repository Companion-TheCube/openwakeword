#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the name of the virtual environment directory
VENV_DIR="."

echo "🔧 Creating virtual environment in: $VENV_DIR"
python3 -m venv "$VENV_DIR"

echo "✅ Virtual environment created."

# Activate the virtual environment
echo "🔁 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "⬆️ Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "⬇️ Installing openwakeword and dependencies..."

# Install OpenWakeWord from PyPI (or optionally from GitHub if you want the latest)
pip install openwakeword

echo "✅ Installation complete."
echo "🎉 OpenWakeWord is now installed and ready to use!"