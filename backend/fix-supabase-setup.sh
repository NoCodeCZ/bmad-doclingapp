#!/bin/bash
# Supabase Setup Fix Script
# This script fixes the package dependency issues and tests the Supabase connection

set -e  # Exit on error

echo "========================================"
echo "SUPABASE SETUP FIX SCRIPT"
echo "========================================"

# Step 1: Navigate to backend directory
echo -e "\n[1/6] Navigating to backend directory..."
cd "$(dirname "$0")"

# Step 2: Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo -e "\n[2/6] Creating virtual environment..."
    python3 -m venv venv
else
    echo -e "\n[2/6] Virtual environment already exists"
fi

# Step 3: Activate virtual environment
echo -e "\n[3/6] Activating virtual environment..."
source venv/bin/activate

# Step 4: Upgrade pip and uninstall conflicting packages
echo -e "\n[4/6] Cleaning up conflicting packages..."
pip install --upgrade pip
pip uninstall -y supabase realtime 2>/dev/null || true

# Step 5: Install requirements
echo -e "\n[5/6] Installing requirements..."
pip install -r requirements.txt

# Step 6: Run Supabase connection test
echo -e "\n[6/6] Testing Supabase connection..."
python tests/test_supabase_connection.py

echo -e "\n========================================"
echo "Setup complete! Next steps:"
echo "========================================"
echo "1. Start backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Test health endpoint:"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "3. Start frontend and test end-to-end:"
echo "   cd frontend"
echo "   npm run dev"
echo "   Visit http://localhost:3000"
echo "========================================"