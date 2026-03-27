#!/usr/bin/env bash
# Quick setup script for JobPilot
set -e

echo "=== JobPilot Setup ==="

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please add your ANTHROPIC_API_KEY."
fi

# Install dependencies
pip install -r requirements.txt

echo ""
echo "=== Setup complete! ==="
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run: uvicorn app.main:app --reload"
echo "3. Open: http://localhost:8000"
