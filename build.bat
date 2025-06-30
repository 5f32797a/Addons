@echo off

echo "Checking for and installing build dependencies..."
pip install --upgrade build

echo "Building project..."
python -m build

echo "Build complete. You can find the artifact s in the 'dist' directory."
pause 