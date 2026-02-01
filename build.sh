#!/bin/bash
# Build script for Render.com

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up database..."
python database.py

echo "Build complete!"
