#!/bin/bash
# TOPAS 3D Visualization Tool - Quick Start Script

echo "=================================================="
echo "TOPAS 3D Visualization Tool - Setup & Demo"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python installation..."
python3 --version

# Install dependencies
echo ""
echo "Installing required packages..."
echo "Run: pip3 install -r requirements.txt"
echo ""
read -p "Install dependencies now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip3 install -r requirements.txt
fi

# Run unit tests
echo ""
echo "Running unit tests..."
python3 python.py --test

# Demo with Cartesian data
echo ""
echo "=================================================="
echo "Demo 1: Cartesian Coordinates"
echo "=================================================="
python3 python.py sample_topas_data.csv -o demo_cartesian --no-display

# Demo with Spherical data
echo ""
echo "=================================================="
echo "Demo 2: Spherical Coordinates"
echo "=================================================="
python3 python.py sample_spherical_data.csv -c spherical -o demo_spherical --no-display

echo ""
echo "=================================================="
echo "✓ Setup Complete!"
echo "=================================================="
echo ""
echo "Output files generated:"
echo "  - demo_cartesian.png"
echo "  - demo_cartesian.html"
echo "  - demo_spherical.png"
echo "  - demo_spherical.html"
echo ""
echo "Open the HTML files in your browser for interactive 3D viewing!"
echo ""
