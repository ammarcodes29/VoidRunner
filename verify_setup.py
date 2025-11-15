#!/usr/bin/env python3
"""
Verification script to ensure VoidRunner is set up correctly.

Run this after installation to check all dependencies and modules.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11+."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.11+ required.")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    required = ["pygame", "numpy", "pytest"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)
    
    return len(missing) == 0


def check_project_structure():
    """Verify project directory structure."""
    required_dirs = [
        "voidrunner",
        "voidrunner/entities",
        "voidrunner/managers",
        "voidrunner/states",
        "voidrunner/ui",
        "voidrunner/utils",
        "voidrunner/assets",
        "tests",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ NOT FOUND")
            all_exist = False
    
    return all_exist


def check_main_files():
    """Check if main Python files exist."""
    required_files = [
        "main.py",
        "voidrunner/game.py",
        "voidrunner/entities/player.py",
        "voidrunner/entities/enemy.py",
        "voidrunner/utils/config.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("VoidRunner Setup Verification")
    print("=" * 60)
    
    print("\n📦 Checking Python Version...")
    python_ok = check_python_version()
    
    print("\n📦 Checking Dependencies...")
    deps_ok = check_dependencies()
    
    print("\n📁 Checking Project Structure...")
    structure_ok = check_project_structure()
    
    print("\n📄 Checking Main Files...")
    files_ok = check_main_files()
    
    print("\n" + "=" * 60)
    
    if python_ok and deps_ok and structure_ok and files_ok:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou're ready to run VoidRunner:")
        print("  python main.py")
        print("\nOr with debug mode:")
        print("  python main.py --debug")
        print("\nRun tests with:")
        print("  pytest")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the game.")
        if not deps_ok:
            print("\nTo install dependencies:")
            print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

