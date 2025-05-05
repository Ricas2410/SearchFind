"""
Installation script for AI dependencies required by the SearchFind AI features.

This script installs the required Python packages for AI functionality:
- PyPDF2 for PDF parsing
- python-docx for DOCX parsing
- nltk for natural language processing

It also downloads the necessary NLTK data.

Usage:
    python scripts/install_ai_dependencies.py
"""

import os
import sys
import subprocess
import platform
import importlib.util

# Required packages and versions
REQUIREMENTS = [
    "PyPDF2==3.0.0",
    "python-docx==0.8.11",
    "nltk==3.8.1"
]

# NLTK data packages needed
NLTK_PACKAGES = [
    "punkt",
    "stopwords",
    "wordnet"
]

def print_step(message):
    """Print a step message with formatting."""
    print(f"\n[AI SETUP] {message}")

def print_success(message):
    """Print a success message with formatting."""
    print(f"\n[SUCCESS] {message}")

def print_error(message):
    """Print an error message with formatting."""
    print(f"\n[ERROR] {message}", file=sys.stderr)

def check_package_installed(package_name):
    """Check if a Python package is installed."""
    package_base = package_name.split('==')[0] if '==' in package_name else package_name
    spec = importlib.util.find_spec(package_base)
    return spec is not None

def install_packages():
    """Install required packages using pip."""
    print_step("Installing required packages...")
    
    # Check which packages are already installed
    packages_to_install = []
    for package in REQUIREMENTS:
        package_base = package.split('==')[0]
        if not check_package_installed(package_base):
            packages_to_install.append(package)
        else:
            print(f"Package {package_base} is already installed.")
    
    if not packages_to_install:
        print_success("All required packages are already installed!")
        return True
    
    # Install missing packages
    cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
    
    try:
        subprocess.check_call(cmd)
        print_success("Successfully installed packages!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install packages: {e}")
        return False

def download_nltk_data():
    """Download required NLTK data."""
    print_step("Downloading NLTK data...")
    
    try:
        import nltk
        for package in NLTK_PACKAGES:
            print(f"Downloading NLTK data: {package}")
            nltk.download(package, quiet=True)
        
        print_success("Successfully downloaded NLTK data!")
        return True
    except Exception as e:
        print_error(f"Failed to download NLTK data: {e}")
        return False

def main():
    """Main entry point for the script."""
    print_step("Starting AI dependencies setup...")
    
    # Install packages
    if not install_packages():
        print_error("Installation failed. Please install the packages manually:")
        for package in REQUIREMENTS:
            print(f"  pip install {package}")
        return 1
    
    # Download NLTK data
    if not download_nltk_data():
        print_error("NLTK data download failed. You can download it manually in Python:")
        for package in NLTK_PACKAGES:
            print(f"  import nltk; nltk.download('{package}')")
        return 1
    
    print_success("""
AI dependencies installation complete!

The AI features are now ready to use. The following components were installed:
- PyPDF2 for PDF parsing
- python-docx for DOCX parsing
- nltk for natural language processing
- nltk data packages: punkt, stopwords, wordnet
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())