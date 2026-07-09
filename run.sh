#!/bin/bash
# ============================================
# Secure File Transfer System - Startup Script
# ============================================
# This script sets up and runs the Flask application

echo ""
echo "========================================"
echo "Secure File Transfer System - Flask App"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install requirements
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "========================================"
echo "Starting Flask Application"
echo "========================================"
echo ""
echo "Access the application at: http://127.0.0.1:5000"
echo ""
echo "Demo Credentials:"
echo "  Username: alice / Password: alice123"
echo "  Username: bob / Password: bob123"
echo "  Username: admin / Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python3 -m flask --app "app:create_app()" run --debug
