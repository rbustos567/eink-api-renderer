#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Installing dependencies for e-Paper Wiki Generator ==="

# 1. Update package lists and install system dependencies
echo "[1/2] Updating apt and installing system packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip fonts-dejavu

# 2. Install Python libraries system-wide
echo "[2/2] Installing Python libraries (Pillow, requests)..."
sudo pip install Pillow requests --break-system-packages

echo ""
echo "=== Installation Complete! ==="
echo "To run your script globally, execute:"
echo "  python3 generate_eink_wiki.py --preset en_tfa"
